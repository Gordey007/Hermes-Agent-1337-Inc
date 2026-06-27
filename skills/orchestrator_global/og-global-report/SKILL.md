---
name: og-global-report
description: Summary report of the global cycle — leads, sprints, successes, sales.
version: 1.0.0
author: hermes-team
license: MIT
metadata:
  hermes:
    requires_toolsets: [sqlite, python]
---

# og-global-report

## WHO
orchestrator_global.

## WHEN
- End of the day/cycle, or an L0 request for a summary.

## STEPS
1. `sqlite-leads`: aggregates — total leads, `is_relevant=1`, `dev_status` by group (`pending`/`in_progress`/`done`/`failed`), `offer_sent`, `reply_status='done'` (payments).
2. kanban: number of sprints, successful/failed, average iterations.
3. Assemble `reports/global_<date>.md`: the funnel (leads→sprints→successes→offers→sales) + links to MinIO reports.

## OUTPUT
- `reports/global_<date>.md` (+ upload to MinIO `hermes-reports/`).

## NEXT
- Available to L0 for monitoring (`l0-monitor`). The cycle continues.

## LIMITS
- Read/aggregation only. Do not include keys (Stripe/X/NVIDIA) in the report.
