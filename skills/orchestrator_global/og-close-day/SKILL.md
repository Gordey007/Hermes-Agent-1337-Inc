---
name: og-close-day
description: Record the outcome in leads and close the cycle — wait for the next tweets/day.
version: 1.0.0
author: hermes-team
license: MIT
metadata:
  hermes:
    requires_toolsets: [sqlite, python]
---

# og-close-day

## WHO
orchestrator_global.

## WHEN
- There are no relevant pending leads, OR the sprint has finished (success/`failed`), OR the outer-loop is exhausted.

## STEPS
1. Record the lead's final status in `leads` (`done`/`failed` + a brief reason).
2. Make sure there are no active sprints (kanban: no `in_progress` root tasks).
3. On `failed` — make sure `reports/` is already in MinIO (`hermes-reports/`) and the working directory has been dropped.

## OUTPUT
- A clean state: no active sprints/containers, lead statuses recorded.

## NEXT
- Finish the cron run. The next cron tick → `og-qualify-lead` on new tweets.

## LIMITS
- Do not start a new sprint in this same run. One project at a time.
