---
name: l0-incident
description: Recovery from failure — a stuck sprint, undeleted containers, a full disk, an expired token.
version: 1.0.0
author: hermes-team
license: MIT
metadata:
  hermes:
    requires_toolsets: [shell, python, sqlite]
---

# l0-incident

## WHO
The main Hermes agent (L0).

## WHEN
- `l0-healthcheck`/`l0-monitor` reported an anomaly.

## STEPS
1. Stuck sprint: find the task in `blocked`/a stuck `in_progress` → initiate `ev-cleanup`
   (drop-all-except-reports) for that `hab_<tweetid>_s<sprint>`, mark the sprint `failed`.
2. Undeleted containers: `docker compose -p hab_<tweetid>_s<sprint> down -v`; general leftovers — `docker container prune`.
3. Full disk: remove the working directories of finished sprints (keeping `reports/`, already in MinIO),
   `docker system prune -f`, clean up `.snap_*`.
4. Expired token: refresh the profile env, restart the cron blueprint; do not log the key.

## OUTPUT
- The system is back to a working state; the incident is recorded in kanban/leads.

## NEXT
- `l0-healthcheck` to confirm. After that, cron continues autonomously.

## LIMITS
- Preserve `reports/` (knowledge carried across days). Do not delete the `leads`/`tasks` DBs. One incident — handle it surgically.
