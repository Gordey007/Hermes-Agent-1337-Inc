---
name: sl-send-x
description: Send the offer via x.com (quote_tweet / send_dm).
version: 1.0.0
author: hermes-team
license: MIT
metadata:
  hermes:
    requires_toolsets: [sqlite, python]
---

# sl-send-x

## WHO
sales.

## WHEN
- The offer is ready (`sl-build-offer`).

## STEPS
1. Choose the channel: `quote_tweet` (public) or `send_dm` (if DMs are open) — per `01_x_lead/x_actions.py`.
2. Send the offer; on an X error/rate limit — defer (do not retry aggressively).
3. `sqlite-leads`: `offer_sent=1`, `reply_status='no_reply'`, update `updated_at`.

## OUTPUT
- The sent offer; `offer_sent=1` in `leads`.

## NEXT
- `sl-stripe-invoice` (prepare the payment link), then `sl-dialog`.

## LIMITS
- ≤1 touch/lead/day. Anti-ban: do not send identical text en masse, respect X's rate limit.
