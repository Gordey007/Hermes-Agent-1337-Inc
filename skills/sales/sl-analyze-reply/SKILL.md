---
name: sl-analyze-reply
description: Analyze the lead's reply → reply_status / reply_summary.
version: 1.0.0
author: hermes-team
license: MIT
metadata:
  hermes:
    requires_toolsets: [sqlite, python]
---

# sl-analyze-reply

## WHO
sales.

## WHEN
- A client reply has arrived on x.com.

## STEPS
1. Read the reply text.
2. Classify the tone/intent: `positive` (interested/ready to pay), `negative` (rejection), neutral (a question).
3. `sqlite-leads`: set `reply_status` (`positive`/`negative`/`no_reply`), record a condensed `reply_summary`.

## OUTPUT
- Updated `reply_status` + `reply_summary` in `leads`.

## NEXT
- positive → `sl-stripe-invoice`/`sl-dialog`; payment → `sl-deliver`; negative → close the lead.

## LIMITS
- Analysis and status recording only. The delivery decision comes after confirmed payment.
