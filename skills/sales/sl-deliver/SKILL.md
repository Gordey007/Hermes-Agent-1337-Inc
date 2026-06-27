---
name: sl-deliver
description: After payment, issue a temporary MinIO presigned link.
version: 1.0.0
author: hermes-team
license: MIT
metadata:
  hermes:
    requires_toolsets: [sqlite, python]
---

# sl-deliver

## WHO
sales.

## WHEN
- A Stripe (TEST) payment for the lead has been confirmed.

## STEPS
1. Verify the payment via Stripe (payment link/invoice status `paid`).
2. `minio-artifacts`: generate a presigned URL for `dev_artifact` with a short TTL.
3. Send the link to the client on x.com (the `sl-send-x` channel).
4. `sqlite-leads`: `reply_status='done'`, record the delivery.

## OUTPUT
- The temporary presigned link sent; `reply_status='done'`.

## NEXT
- The lead is complete → orchestrator_global (`og-close-day`/`og-global-report`).

## LIMITS
- I issue the link ONLY after confirmed payment. Short TTL. I do not hand the permanent MinIO key outside.
