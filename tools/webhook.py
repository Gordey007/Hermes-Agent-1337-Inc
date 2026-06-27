# ~/tools/webhook.py
import os, stripe, boto3
from botocore.client import Config
from flask import Flask, request

stripe.api_key = os.environ["STRIPE_API_KEY_TEST"]
WHSEC = os.environ["STRIPE_WEBHOOK_SECRET"]

s3 = boto3.client(
    "s3",
    endpoint_url=os.environ.get("MINIO_ENDPOINT", "http://172.18.0.1:9000"),
    aws_access_key_id=os.environ["MINIO_ACCESS_KEY"],
    aws_secret_access_key=os.environ["MINIO_SECRET_KEY"],
    config=Config(signature_version="s3v4"),
    region_name="us-east-1",
)

app = Flask(__name__)

@app.post("/webhook")
def hook():
    event = stripe.Webhook.construct_event(
        request.data, request.headers.get("Stripe-Signature"), WHSEC)

    if event["type"] == "checkout.session.completed":
        s = event["data"]["object"]
        minio_key = s.get("metadata", {}).get("minio_key", "")
        if not minio_key:
            print("no minio_key in metadata — skipping")
            return "", 200
        # format "bucket/object/path.zip" -> bucket + key
        bucket, _, key = minio_key.partition("/")
        url = s3.generate_presigned_url(
            "get_object",
            Params={"Bucket": bucket, "Key": key},
            ExpiresIn=3600,  # 1 hour
        )
        print(f"✅ PAID session={s['id']}")
        print(f"   link for the buyer ({s.get('customer_details',{}).get('email')}):")
        print(f"   {url}")
        # here send it to the buyer (email / telegram / Hermes response)
    return "", 200

app.run(port=4242)