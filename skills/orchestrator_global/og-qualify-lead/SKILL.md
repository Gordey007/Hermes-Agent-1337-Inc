---
name: og-qualify-lead
description: Read leads, assess tweet relevance, set is_relevant.
version: 1.0.0
author: hermes-team
license: MIT
metadata:
  hermes:
    requires_toolsets: [sqlite, python]
---

# og-qualify-lead

## WHO
orchestrator_global (L1, cron).

## WHEN
- Start of the cron cycle: there are rows with `is_relevant IS NULL` (or `=0 AND dev_status='pending'`).

## STEPS
1. `sqlite-leads`: read candidates (`SELECT ... WHERE is_relevant IS NULL ORDER BY impression_count DESC`).
2. Assess the tweet: a clear need for a product/tool, willingness to pay, not a bot (`is_bot`/`bot_score`).
3. Set: relevant → `is_relevant=1` (→ `dev_status='pending'`); otherwise `is_relevant=0`.

## OUTPUT
- Updated `is_relevant` + `updated_at` in `leads`.

## NEXT
- There are relevant pending leads → `og-pick-task`. None → `og-close-day`.

## LIMITS
- You may qualify in batches; only ONE lead is taken into work per run (see og-pick-task). Filter out bots.
