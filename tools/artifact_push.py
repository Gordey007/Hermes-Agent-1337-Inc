#!/usr/bin/env python3
"""
artifact_push.py — Hermes tool: package a delivery directory and upload it to MinIO (S3),
returning a presigned link for the client.

Why: the sandbox has no aws-cli/zip; boto3 is installed via pip and respects HTTP_PROXY,
so all S3 traffic goes through the OpenShell forward proxy automatically.

Dependencies (installed once in the sandbox):
    pip install --user boto3        # or: uv pip install boto3

Environment variables (read automatically):
    MINIO_ROOT_USER / MINIO_ROOT_PASSWORD   — MinIO credentials (S3 access/secret key)
    HTTP_PROXY=http://10.200.0.1:3128        — OpenShell forward proxy (boto3 honors it)
    S3_ENDPOINT  (opt.)  — defaults to http://172.18.0.1:9000

Examples:
    # package a directory and upload, get a link valid for 7 days
    python tools/artifact_push.py /sandbox/demo/notes_api \
        --bucket hermes-artifacts --key hab_demo/v1/notes_api.zip --expire 168h

    # upload an already-prepared file
    python tools/artifact_push.py /tmp/notes_api.zip \
        --bucket hermes-artifacts --key hab_demo/v1/notes_api.zip
"""
from __future__ import annotations

import argparse
import os
import re
import shutil
import sys
import tempfile

import boto3
from botocore.client import Config

from dotenv import load_dotenv
load_dotenv()


def parse_expire(s: str) -> int:
    """'168h' / '30m' / '3600' -> seconds."""
    m = re.fullmatch(r"(\d+)([smhd]?)", s.strip())
    if not m:
        raise argparse.ArgumentTypeError(f"invalid TTL format: {s!r}")
    n, unit = int(m.group(1)), m.group(2)
    return n * {"": 1, "s": 1, "m": 60, "h": 3600, "d": 86400}[unit]


def make_zip(src_dir: str) -> str:
    """Package a directory so the archive contains its folder (src_dir/...)."""
    src_dir = os.path.abspath(src_dir.rstrip("/\\"))
    parent, name = os.path.split(src_dir)
    out_base = os.path.join(tempfile.gettempdir(), name)
    archive = shutil.make_archive(out_base, "zip", root_dir=parent, base_dir=name)
    return archive


def s3_client(endpoint: str, verify: bool = True):
    user = os.environ.get("MINIO_ROOT_USER")
    secret = os.environ.get("MINIO_ROOT_PASSWORD")
    if not (user and secret):
        sys.exit("No MINIO_ROOT_USER / MINIO_ROOT_PASSWORD in the environment.")
    # boto3 will pick up HTTP_PROXY/HTTPS_PROXY from the environment on its own.
    # verify=False — when the OpenShell forward proxy terminates TLS on REST hosts
    # (substituting the MinIO certificate), we disable chain verification.
    client = boto3.client(
        "s3",
        endpoint_url=endpoint,
        aws_access_key_id=user,
        aws_secret_access_key=secret,
        config=Config(
            signature_version="s3v4",
            s3={"addressing_style": "path"},
            # boto3>=1.36 by default sends PUT as aws-chunked + a streaming CRC32 trailer
            # (Transfer-Encoding: chunked). The OpenShell L7 proxy breaks such a stream
            # (RemoteDisconnected). We disable auto-checksum -> a plain PUT with Content-Length.
            request_checksum_calculation="when_required",
            response_checksum_validation="when_required",
        ),
        region_name="us-east-1",
        verify=verify,
    )

    # The proxy dislikes Expect: 100-continue and the internal amz-sdk-* headers —
    # we strip them before sending (this doesn't affect the SigV4 signature: they aren't signed).
    def _strip_headers(request, **_):
        for h in ("Expect", "amz-sdk-invocation-id", "amz-sdk-request"):
            request.headers.pop(h, None)
    client.meta.events.register("before-send.s3.*", _strip_headers)
    return client


def main() -> int:
    p = argparse.ArgumentParser(description="Upload an artifact to MinIO and return a presigned URL.")
    p.add_argument("path", help="path to the delivery file or directory")
    p.add_argument("--bucket", default="hermes-artifacts")
    p.add_argument("--key", required=True, help="object key in the bucket, e.g. hab_demo/v1/notes_api.zip")
    p.add_argument("--endpoint", default=os.environ.get("S3_ENDPOINT", "http://172.18.0.1:9000"),
                   help="S3 endpoint for upload (internal bridge/proxy)")
    p.add_argument("--public-endpoint", default=os.environ.get("S3_PUBLIC_ENDPOINT"),
                   help="public S3 endpoint for the presigned link (signature is bound to host)")
    p.add_argument("--presign-only", action="store_true",
                   help="don't upload, just generate a presigned URL for an existing object")
    p.add_argument("--insecure", action="store_true", default=True,
                   help="don't verify the TLS certificate (the OpenShell proxy terminates TLS); on by default")
    p.add_argument("--expire", type=parse_expire, default=parse_expire("168h"),
                   help="presigned link TTL, e.g. 168h/30m/3600 (default 7 days)")
    p.add_argument("--no-url", action="store_true", help="don't print the presigned URL")
    args = p.parse_args()

    # --presign-only: only sign a link for an already-uploaded object, no upload.
    if not args.presign_only:
        # 1) if it's a directory — package into a zip
        if os.path.isdir(args.path):
            local_file = make_zip(args.path)
            print(f"[zip]  {args.path} -> {local_file}", file=sys.stderr)
        elif os.path.isfile(args.path):
            local_file = args.path
        else:
            sys.exit(f"Path not found: {args.path}")

        s3 = s3_client(args.endpoint, verify=not args.insecure)

        # 2) bucket (create if missing — idempotent)
        try:
            s3.head_bucket(Bucket=args.bucket)
        except Exception:
            s3.create_bucket(Bucket=args.bucket)
            print(f"[s3]   created bucket {args.bucket}", file=sys.stderr)

        # 3) upload
        # IMPORTANT: don't use upload_file/s3transfer — it sends PUT as a stream
        # (Transfer-Encoding: chunked / aws-chunked), and the OpenShell L7 proxy breaks
        # such a stream (RemoteDisconnected). We read the whole file into memory and send
        # put_object(Body=<bytes>) — botocore sets Content-Length, exactly like
        # `curl --data-binary` (which passes through the proxy).
        with open(local_file, "rb") as f:
            data = f.read()
        s3.put_object(Bucket=args.bucket, Key=args.key, Body=data)
        print(f"[s3]   uploaded s3://{args.bucket}/{args.key} ({len(data)} bytes)", file=sys.stderr)

    # 4) presigned URL for the client.
    # The SigV4 signature includes host, so we sign the link under the endpoint
    # the client will actually download from. If --public-endpoint is given —
    # we use a separate client with the public address (no network call when signing).
    if not args.no_url:
        presign_endpoint = args.public_endpoint or args.endpoint
        presigner = s3_client(presign_endpoint, verify=not args.insecure)
        url = presigner.generate_presigned_url(
            "get_object",
            Params={"Bucket": args.bucket, "Key": args.key},
            ExpiresIn=args.expire,
        )
        print(url)
    return 0


if __name__ == "__main__":
    sys.exit(main())
