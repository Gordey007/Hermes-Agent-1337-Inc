---
name: sl-build-offer
description: Compose a personalized offer from the tweet text + what was built.
version: 1.0.0
author: hermes-team
license: MIT
metadata:
  hermes:
    requires_toolsets: [sqlite, python]
---

# sl-build-offer

## WHO
sales.

## WHEN
- `dev_status='done'`, `dev_artifact` is set (handed off from `og-handoff-sales`).

## STEPS
1. Read the lead (`sqlite-leads`): tweet text, author, `dev_artifact` (MinIO key).
2. Read `reports/final.md` (what was built, working examples).
3. Compose a short personalized offer: the problem from the tweet → what was done → the value. Soft tone, no spam, ≤1 message.

## OUTPUT
- The offer text (a draft to send), tied to `tweet_id`.

## NEXT
- `sl-send-x`.

## LIMITS
- I do not touch development. One offer per lead. No aggressive wording (anti-ban).
