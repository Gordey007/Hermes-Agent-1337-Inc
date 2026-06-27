---
name: og-pick-task
description: Pick one simplest suitable lead → dev_status='in_progress'.
version: 1.0.0
author: hermes-team
license: MIT
metadata:
  hermes:
    requires_toolsets: [sqlite, python]
---

# og-pick-task

## WHO
orchestrator_global.

## WHEN
- There are relevant `dev_status='pending'` leads and no active sprint (one project at a time).

## STEPS
1. `sqlite-leads`: select candidates `is_relevant=1 AND dev_status='pending'`.
2. Assess the SIMPLICITY of implementation (a minimal product for the need) — pick the most achievable one.
3. Take one: `UPDATE leads SET dev_status='in_progress', updated_at=datetime('now') WHERE tweet_id='<ID>';`

## OUTPUT
- One lead in `dev_status='in_progress'` — a candidate for the sprint.

## NEXT
- `og-author-dod` (draft the initial DoD from the tweet text).

## LIMITS
- Exactly ONE lead per run. Prefer the simple and achievable over the complex.
