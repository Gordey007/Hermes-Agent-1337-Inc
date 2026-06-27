---
name: sl-stripe-invoice
description: Create a Stripe invoice (TEST key) on top of stripe-link-cli.
version: 1.0.0
author: hermes-team
license: MIT
metadata:
  hermes:
    requires_toolsets: [shell, python]
---

# sl-stripe-invoice

## WHO
sales.

## WHEN
- The offer has been sent (`sl-send-x`) or the client showed interest (`sl-analyze-reply` → positive).

## STEPS
1. Create a payment link/invoice via `02_sales_pipeline/stripe_offer.py` (on top of `stripe-link-cli`), using **ONLY** `STRIPE_API_KEY_TEST` (`sk_test_...`).
2. Tie the amount/description to the lead's product; save the payment link in `leads`.
3. `sqlite-leads`: save the payment link in the lead's field.

## OUTPUT
- A Stripe TEST payment link, saved in `leads`.

## NEXT
- `sl-dialog` (pass the link to the client at the right moment).

## LIMITS
- It is **FORBIDDEN** to use a live key (`rk_live_`/`sk_live_`). NEVER log keys or send them outside. TEST mode only.
