---
name: os-teardown
description: Trigger ev-cleanup (drop-all-except-reports) and close the sprint.
version: 1.0.0
author: hermes-team
license: MIT
metadata:
  hermes:
    requires_toolsets: [shell, python, sqlite]
---

# os-teardown

## WHO
orchestrator_sprint.

## WHEN
- The sprint has finished (`done` or `failed`), and the evaluator has already uploaded `reports/` to MinIO.

## STEPS
1. Make sure `ev-cleanup` has run: `docker compose -p hab_<tweetid>_s<sprint> down -v`, containers removed.
2. Confirm that nothing remains in the working directory except `reports/` (research/design/product dropped).
3. Close the sprint's root kanban task (`done`/`failed`) + a brief summary.

## OUTPUT
- The torn-down stack, a cleaned directory (only `reports/`), the closed sprint.

## NEXT
- Return control to orchestrator_global (`done` → `og-handoff-sales`; `failed` → `og-refine-dod`/`og-close-day`).

## LIMITS
- NEVER delete `reports/` or the DB (`leads`/`tasks`). Only this sprint project.
