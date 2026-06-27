---
name: sl-dialog
description: Hold an unobtrusive dialog with the lead (≤1 touch/day, soft tone).
version: 1.0.0
author: hermes-team
license: MIT
metadata:
  hermes:
    requires_toolsets: [sqlite, python]
---

# sl-dialog

## WHO
sales.

## WHEN
- The offer has been sent; there is a reply or the cooldown has expired.

## STEPS
1. Check the cooldown: enough time has passed since `updated_at` (no more than 1 touch/lead/day).
2. If there is a new client reply → first `sl-analyze-reply`.
3. Reply softly: answer the question and, when they're ready, give the Stripe link (`sl-stripe-invoice`). No pressure.
4. `sqlite-leads`: update `updated_at` and, if needed, `reply_summary`.

## OUTPUT
- The sent dialog message; `updated_at` updated.

## NEXT
- `sl-analyze-reply` (on a reply) or `sl-deliver` (after payment).

## LIMITS
- ≤1 touch/lead/day, cooldown based on `updated_at`. I don't push, I don't spam. I don't touch development.
