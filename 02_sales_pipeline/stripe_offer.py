"""Stripe-invoice for salespeople: create an invoice for a ready-made product (TEST key).

One lead = one product = one invoice. After payment: webhook/poll → presigned link
MinIO (see minio_client.py). Uses the sl-stripe-invoice skill on top of stripe-link-cli.

SECURITY: Use ONLY the key from the STRIPE_API_KEY_TEST environment variable (sk_test_...). NEVER use
a live key for offline invoicing during the hackathon. The key is not logged or committed.
"""

from __future__ import annotations

import os
import sys

import stripe

from dotenv import load_dotenv
load_dotenv()

# TODO: use live key in production
# API_KEY = os.getenv("STRIPE_API_KEY", "")
API_KEY = os.getenv("STRIPE_API_KEY_TEST", "")
CURRENCY = os.getenv("STRIPE_CURRENCY", "usd")


# TODO: use live key in production
def _client():
    if stripe is None:
        sys.exit("stripe is not installed: pip install stripe")
    if not API_KEY.startswith("sk_test_"):
        sys.exit("STRIPE_API_KEY_TEST must be a TEST key (sk_test_...) — live prohibited")
    stripe.api_key = API_KEY
    return stripe


def create_invoice(email: str, product_name: str, amount_usd: float,
                   description: str = "", days_until_due: int = 7) -> dict:
    """Create customer + invoice item + invoice, finalize → return payment link."""
    s = _client()
    customer = s.Customer.create(email=email, description=f"hermes lead: {product_name}")
    s.InvoiceItem.create(
        customer=customer.id,
        amount=int(round(amount_usd * 100)),  # cents
        currency=CURRENCY,
        description=description or product_name,
    )
    invoice = s.Invoice.create(
        customer=customer.id,
        collection_method="send_invoice",
        days_until_due=days_until_due,
        metadata={"product": product_name},
    )
    invoice = s.Invoice.finalize_invoice(invoice.id)
    return {
        "invoice_id": invoice.id,
        "customer_id": customer.id,
        "status": invoice.status,
        "hosted_invoice_url": invoice.hosted_invoice_url,
        "amount_due": invoice.amount_due / 100,
    }


def check_paid(invoice_id: str) -> dict:
    """Check payment status (sl-dialog / sl-deliver: pay → deliver presigned link)."""
    s = _client()
    inv = s.Invoice.retrieve(invoice_id)
    return {"invoice_id": invoice_id, "status": inv.status,
            "paid": inv.status == "paid", "amount_paid": inv.amount_paid / 100}


if __name__ == "__main__":
    import argparse
    import json
    ap = argparse.ArgumentParser(description="Stripe invoice (TEST)")
    sub = ap.add_subparsers(dest="cmd", required=True)
    c = sub.add_parser("create")
    c.add_argument("--email", required=True); c.add_argument("--product", required=True)
    c.add_argument("--amount", type=float, required=True); c.add_argument("--desc", default="")
    k = sub.add_parser("check"); k.add_argument("--invoice", required=True)
    args = ap.parse_args()
    if args.cmd == "create":
        print(json.dumps(create_invoice(args.email, args.product, args.amount, args.desc),
                         ensure_ascii=False, indent=2))
    elif args.cmd == "check":
        print(json.dumps(check_paid(args.invoice), ensure_ascii=False, indent=2))
