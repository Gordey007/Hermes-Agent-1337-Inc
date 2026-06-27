"""Sales API for the Hermes agent: publish artifact + payment (Stripe Checkout) + delivery.

Hermes calls the endpoints in sequence:
  1. POST /artifacts          -> zip a LOCAL sandbox dir, upload to MinIO, get minio_key
  2. POST /payments           -> create a payment for that minio_key, get checkout_url + session_id
  3. GET  /payments/<id>      -> check status, wait for "paid"
  4. POST /download-link      -> once paid, activate the stable delivery link /d/<token>
  5. GET  /d/<token>          -> download the artifact (streamed from MinIO), single window

Outreach (DM / quote-tweet) is intentionally NOT part of this API; it lives in
`x_actions.py` and the `sl-send-x` sales skill. This service does one thing:
turn a built artifact into a paid, time-boxed download.

SECURITY:
  - Only a Stripe TEST key (sk_test_...) from STRIPE_API_KEY_TEST is accepted. Live keys are
    rejected at startup of every Stripe call. The key is never logged.
  - /download-link does NOT trust the caller: the payment status is re-checked in Stripe
    (session.payment_status == "paid") and the object key is read from the paid session's
    metadata, not from the request body — you cannot pay for one file and download another.

MinIO / S3 (proxy-safe path, see tools/artifact_push.py):
  - Upload uses boto3 put_object(Body=<bytes>) with stripped headers. The sandbox L7 proxy
    breaks chunked/aws-chunked PUT, so the file is read fully into memory and sent as a plain
    PUT with Content-Length.
  - Creds: MINIO_ROOT_USER / MINIO_ROOT_PASSWORD
  - S3_ENDPOINT         (internal bridge used for upload)
  - S3_PUBLIC_ENDPOINT  (optional) — host the buyer downloads from; presigned URLs bind to it.

Run:  uv run api.py    (listens on 0.0.0.0:$PORT, default 8000)
"""


from __future__ import annotations

import os
import re
import shutil
import sys
import tempfile
import time
import threading

import stripe

import boto3
from botocore.client import Config

from flask import Flask, Response, jsonify, request

from dotenv import load_dotenv
load_dotenv()

API_KEY = os.getenv("STRIPE_API_KEY_TEST", "")
CURRENCY = os.getenv("STRIPE_CURRENCY", "usd")
SUCCESS_URL = os.getenv("STRIPE_SUCCESS_URL", "https://example.com/thank-you")
CANCEL_URL = os.getenv("STRIPE_CANCEL_URL", "https://example.com/canceled")
PRESIGN_TTL_MINUTES = int(os.getenv("PRESIGN_TTL_MINUTES", "3"))  # download link validity window

# Offer is fixed server-side so the caller can only supply minio_key, never the price.
OFFER_NAME = os.getenv("OFFER_NAME", "Hermes — built-to-order project")
OFFER_DESCRIPTION = os.getenv(
    "OFFER_DESCRIPTION",
    "TEST PAYMENT ONLY. Stripe runs in TEST mode — no real money is charged. "
    "Use the test card 4242 4242 4242 4242 with any future expiry and CVC. "
    "Do NOT enter real card numbers or personal data.",
)
OFFER_AMOUNT = float(os.getenv("OFFER_AMOUNT", "69.42"))  # USD

S3_ENDPOINT = os.getenv("S3_ENDPOINT", "http://127.0.0.1:9000")
S3_PUBLIC_ENDPOINT = os.getenv("S3_PUBLIC_ENDPOINT")  # host the buyer downloads from
ARTIFACTS_BUCKET = os.getenv("MINIO_ARTIFACTS_BUCKET", "hermes-artifacts")
PUBLIC_BASE_URL = os.getenv("PUBLIC_BASE_URL", "http://localhost:8000")  # public origin of /d/<token>

app = Flask(__name__)

# Delivery tokens, activated ONLY after a confirmed payment (via /download-link).
# token -> {"session_id": str, "expires_at": epoch_seconds}.
# /d/<token> stays valid (and re-openable) for PRESIGN_TTL_MINUTES; each open re-checks
# the payment and streams a fresh copy. In-memory: cleared on restart.
_LINKS: dict[str, dict] = {}
_LINKS_LOCK = threading.Lock()


# --------------------------------------------------------------------------- Stripe

def _client():
    if stripe is None:
        sys.exit("stripe is not installed: pip install stripe")
    if not API_KEY.startswith("sk_test_"):
        sys.exit("STRIPE_API_KEY_TEST must be a TEST key (sk_test_...) — live prohibited")
    stripe.api_key = API_KEY
    # The sandbox forward-proxy terminates TLS with a self-signed cert, so the SDK's default
    # chain verification fails (CERTIFICATE_VERIFY_FAILED). Same reason boto3 uses verify=False.
    # TEST mode only — no live secrets ever pass through here.
    stripe.verify_ssl_certs = False
    proxy = os.environ.get("HTTPS_PROXY") or os.environ.get("HTTP_PROXY")
    if proxy:
        stripe.proxy = proxy
    return stripe


# -------------------------------------------------------------- MinIO / S3 (boto3, proxy-safe)

def _s3(endpoint: str | None = None):
    """boto3 S3 client tuned for the sandbox forward-proxy (same as tools/artifact_push.py)."""
    if boto3 is None:
        sys.exit("boto3 is not installed: pip install boto3")
    user = os.environ.get("MINIO_ROOT_USER")
    secret = os.environ.get("MINIO_ROOT_PASSWORD")
    if not (user and secret):
        sys.exit("MINIO_ROOT_USER / MINIO_ROOT_PASSWORD missing in environment")
    client = boto3.client(
        "s3",
        endpoint_url=endpoint or S3_ENDPOINT,
        aws_access_key_id=user,
        aws_secret_access_key=secret,
        config=Config(
            signature_version="s3v4",
            s3={"addressing_style": "path"},
            request_checksum_calculation="when_required",
            response_checksum_validation="when_required",
        ),
        region_name="us-east-1",
        # verify=False,  # proxy terminates TLS for REST hosts
    )

    def _strip_headers(request, **_):
        for h in ("Expect", "amz-sdk-invocation-id", "amz-sdk-request"):
            request.headers.pop(h, None)

    client.meta.events.register("before-send.s3.*", _strip_headers)
    return client


def _make_zip(src_dir: str) -> str:
    """Zip a directory so the archive contains its own folder (src_dir/...)."""
    src_dir = os.path.abspath(os.path.expanduser(src_dir.rstrip("/\\")))
    parent, name = os.path.split(src_dir)
    out_base = os.path.join(tempfile.gettempdir(), name)
    return shutil.make_archive(out_base, "zip", root_dir=parent, base_dir=name)


def _slugify(s: str) -> str:
    return re.sub(r"[^a-zA-Z0-9._-]+", "-", s).strip("-") or "artifact"


def _meta_minio_key(session) -> str | None:
    """Read metadata.minio_key safely. Stripe's StripeObject has no .get(); use key access."""
    meta = session.metadata or {}
    return meta["minio_key"] if "minio_key" in meta else None


def _split_key(minio_key: str) -> tuple[str, str]:
    """'bucket/path/to/file.zip' -> ('bucket', 'path/to/file.zip')."""
    bucket, _, key = minio_key.partition("/")
    if not bucket or not key:
        raise ValueError(f"minio_key must be of the form 'bucket/object', got: {minio_key!r}")
    return bucket, key


# --------------------------------------------------------------- Core helpers (shared by endpoints)

def _upload_artifact(path: str, bucket: str | None = None, key: str | None = None) -> tuple[str, int]:
    """Zip a local dir (or take a file as-is) and upload it to MinIO. Returns (minio_key, size)."""
    path = os.path.expanduser(path)
    if os.path.isdir(path):
        local_file = _make_zip(path)
    elif os.path.isfile(path):
        local_file = path
    else:
        raise FileNotFoundError(f"path not found: {path}")

    bucket = bucket or ARTIFACTS_BUCKET
    if not key:
        key = f"hab_demo/v1/{_slugify(os.path.basename(local_file))}"

    with open(local_file, "rb") as f:
        body = f.read()

    s3 = _s3()
    try:
        s3.head_bucket(Bucket=bucket)
    except Exception:
        s3.create_bucket(Bucket=bucket)
    s3.put_object(Bucket=bucket, Key=key, Body=body)
    return f"{bucket}/{key}", len(body)


def _create_checkout(minio_key: str):
    """Create a Stripe Checkout Session for a MinIO object. Returns the session."""
    s = _client()
    return s.checkout.Session.create(
        mode="payment",
        success_url=SUCCESS_URL,
        cancel_url=CANCEL_URL,
        line_items=[{
            "price_data": {
                "currency": CURRENCY,
                "product_data": {"name": OFFER_NAME, "description": OFFER_DESCRIPTION},
                "unit_amount": int(round(OFFER_AMOUNT * 100)),
            },
            "quantity": 1,
        }],
        metadata={"minio_key": minio_key},
    )


def _minio_key_for_session(session_id: str) -> str:
    """Verify the session is paid, then return its minio_key.

    Raises ValueError on any failure (caller maps it to an HTTP error).
    """
    session = _client().checkout.Session.retrieve(session_id)
    if session.payment_status != "paid":
        raise ValueError(f"not paid:{session.payment_status}")
    minio_key = _meta_minio_key(session)
    if not minio_key:
        raise ValueError("no_minio_key")
    return minio_key


# --------------------------------------------------------------------------- Endpoints

@app.post("/artifacts")
def publish_artifact():
    """Zip a LOCAL sandbox path and upload it to MinIO; return the minio_key.

    body: {"path": "~/demo/notes_api",         # local dir or file
           "bucket": "hermes-artifacts",        # optional
           "key": "hab_demo/v1/notes_api.zip"}  # optional, auto-generated if absent

    -> {"minio_key": "hermes-artifacts/hab_demo/v1/notes_api.zip", "size_bytes": ...}
    Feed the returned minio_key into POST /payments.
    """
    data = request.get_json(force=True, silent=True) or {}
    path = data.get("path")
    if not path:
        return jsonify(error="path is required (local sandbox dir or file)"), 400
    try:
        minio_key, size = _upload_artifact(path, data.get("bucket"), data.get("key"))
    except FileNotFoundError as e:
        return jsonify(error=str(e)), 400
    bucket, key = _split_key(minio_key)
    return jsonify(minio_key=minio_key, bucket=bucket, key=key, size_bytes=size)


@app.post("/payments")
def create_payment():
    """Create a Checkout Session for a specific file in MinIO.

    body: {"minio_key": "hermes-artifacts/hab_demo/v1/notes_api.zip"}
    Name, description and amount are fixed server-side — the caller only supplies minio_key.
    """
    data = request.get_json(force=True, silent=True) or {}
    minio_key = data.get("minio_key")
    if not minio_key:
        return jsonify(error="minio_key is required (publish it first via POST /artifacts)"), 400

    session = _create_checkout(minio_key)
    return jsonify(
        session_id=session.id,
        checkout_url=session.url,
        payment_status=session.payment_status,  # "unpaid"
        amount=OFFER_AMOUNT,
        minio_key=minio_key,
    )


@app.get("/payments/<session_id>")
def payment_status(session_id: str):
    """Poll payment status (the caller polls until paid=true)."""
    session = _client().checkout.Session.retrieve(session_id)
    return jsonify(
        session_id=session.id,
        payment_status=session.payment_status,   # unpaid | paid | no_payment_required
        paid=session.payment_status == "paid",
        minio_key=_meta_minio_key(session),
    )


@app.post("/download-link")
def download_link():
    """Activate the stable delivery link /d/<token> — ONLY if the session is paid.

    body: {"session_id": "cs_test_...", "token": "<optional stable id>"}
    `token` is a stable, known-in-advance id; if omitted, the session_id is used. After
    this call, /d/<token> stays valid for PRESIGN_TTL_MINUTES and can be re-opened.
    """
    data = request.get_json(force=True, silent=True) or {}
    session_id = data.get("session_id")
    if not session_id:
        return jsonify(error="session_id is required"), 400
    token = str(data.get("token") or session_id)

    try:
        minio_key = _minio_key_for_session(session_id)
    except ValueError as e:
        if str(e).startswith("not paid:"):
            return jsonify(error="not paid", payment_status=str(e).split(":", 1)[1]), 402
        return jsonify(error=str(e)), 500

    with _LINKS_LOCK:
        _LINKS[token] = {"session_id": session_id, "expires_at": time.time() + PRESIGN_TTL_MINUTES * 60}

    return jsonify(
        session_id=session_id,
        minio_key=minio_key,
        download_url=f"{PUBLIC_BASE_URL}/d/{token}",
        expires_in_minutes=PRESIGN_TTL_MINUTES,
    )


@app.get("/d/<token>")
def deliver(token: str):
    """Stable delivery link. Active only after /download-link confirmed the payment.

    Valid for PRESIGN_TTL_MINUTES and re-openable. The file is streamed straight through
    this API from MinIO (no redirect to an internal MinIO host), so it downloads from the
    same public origin.
    """
    with _LINKS_LOCK:
        entry = _LINKS.get(token)
        if not entry or time.time() > entry["expires_at"]:
            _LINKS.pop(token, None)
            return jsonify(error="link not active or expired"), 410
        session_id = entry["session_id"]

    try:
        minio_key = _minio_key_for_session(session_id)
        bucket, key = _split_key(minio_key)
        obj = _s3().get_object(Bucket=bucket, Key=key)
    except ValueError as e:
        if str(e).startswith("not paid:"):
            return jsonify(error="payment not completed yet"), 402
        return jsonify(error=str(e)), 410
    except Exception as e:  # Stripe/boto errors must not surface as a bare 500
        return jsonify(error=f"delivery failed: {e}"), 502

    filename = os.path.basename(key) or "artifact.zip"
    body = obj["Body"]
    headers = {
        "Content-Disposition": f'attachment; filename="{filename}"',
        "Content-Type": obj.get("ContentType") or "application/octet-stream",
    }
    if obj.get("ContentLength") is not None:
        headers["Content-Length"] = str(obj["ContentLength"])
    return Response(body.iter_chunks(chunk_size=64 * 1024), headers=headers)


@app.get("/health")
def health():
    return jsonify(ok=True)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.getenv("PORT", "8000")))
