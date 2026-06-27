"""Public single-use delivery service. Runs ON THE VPS next to Caddy and MinIO.

The Hermes sales API (api.py) lives inside the OpenShell sandbox and is NOT reachable
from the outside — so it cannot serve public download links. This tiny service does:

  GET /d/<session_id>  ->  verify the Stripe session is paid, presign the MinIO object
                           (bound to the public CDN host), 302-redirect, single-use.

It shares nothing with the sandbox except the same Stripe account and the same MinIO.
Caddy routes /d/* here; everything else goes straight to MinIO.

SECURITY:
  - TEST Stripe key only (sk_test_...). The object key comes from the paid session's
    metadata, never from the client — you cannot pay for one file and fetch another.
  - Single-use: the first successful hit burns the token; later hits get 410.
"""

from __future__ import annotations

import os
import sys
import time
import threading

import stripe
import boto3
from botocore.client import Config
from flask import Flask, jsonify, redirect

API_KEY = os.environ.get("STRIPE_API_KEY_TEST", "")
S3_PUBLIC_ENDPOINT = os.environ.get("S3_PUBLIC_ENDPOINT", "")
PRESIGN_TTL_MINUTES = int(os.getenv("PRESIGN_TTL_MINUTES", "3"))

if not API_KEY:
    sys.exit("STRIPE_API_KEY_TEST is required (test key, sk_test_...)")
if not S3_PUBLIC_ENDPOINT:
    sys.exit("S3_PUBLIC_ENDPOINT is required (public host the buyer downloads from)")

app = Flask(__name__)
_LINKS: dict[str, dict] = {}
_LINKS_LOCK = threading.Lock()


def _stripe():
    if not API_KEY.startswith("sk_test_"):
        sys.exit("STRIPE_API_KEY_TEST must be a TEST key (sk_test_...) — live prohibited")
    stripe.api_key = API_KEY
    return stripe


def _s3():
    user = os.environ.get("MINIO_ROOT_USER")
    secret = os.environ.get("MINIO_ROOT_PASSWORD")
    if not (user and secret):
        sys.exit("MINIO_ROOT_USER / MINIO_ROOT_PASSWORD missing in environment")
    return boto3.client(
        "s3",
        endpoint_url=S3_PUBLIC_ENDPOINT,
        aws_access_key_id=user,
        aws_secret_access_key=secret,
        config=Config(signature_version="s3v4", s3={"addressing_style": "path"}),
        region_name="us-east-1",
    )


def _presign_for_session(session_id: str) -> str:
    session = _stripe().checkout.Session.retrieve(session_id)
    if session.payment_status != "paid":
        raise ValueError(f"not paid:{session.payment_status}")
    meta = session.metadata or {}
    minio_key = meta["minio_key"] if "minio_key" in meta else None
    if not minio_key:
        raise ValueError("no_minio_key")
    bucket, _, key = minio_key.partition("/")
    if not bucket or not key:
        raise ValueError("bad_minio_key")
    return _s3().generate_presigned_url(
        "get_object",
        Params={"Bucket": bucket, "Key": key},
        ExpiresIn=PRESIGN_TTL_MINUTES * 60,
    )


@app.get("/d/<session_id>")
def deliver(session_id: str):
    with _LINKS_LOCK:
        entry = _LINKS.get(session_id)
        if entry and (entry["used"] or time.time() > entry["expires_at"]):
            return jsonify(error="link expired or already used"), 410
    try:
        url = _presign_for_session(session_id)
    except ValueError as e:
        if str(e).startswith("not paid:"):
            return jsonify(error="not paid", payment_status=str(e).split(":", 1)[1]), 402
        return jsonify(error=str(e)), 410
    with _LINKS_LOCK:
        _LINKS[session_id] = {"expires_at": time.time() + PRESIGN_TTL_MINUTES * 60, "used": True}
    return redirect(url, code=302)


@app.get("/health")
def health():
    return jsonify(ok=True)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.getenv("PORT", "8000")))
