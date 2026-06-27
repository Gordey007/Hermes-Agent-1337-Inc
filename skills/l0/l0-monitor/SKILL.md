---
name: l0-monitor
description: Monitor the autonomous system — kanban (sprints/tasks), leads, MinIO reports, profile statuses.
version: 1.0.0
author: hermes-team
license: MIT
metadata:
  hermes:
    requires_toolsets: [shell, python, sqlite]
---

# l0-monitor

## WHO
The main Hermes agent (L0) / a human operator.

## WHEN
- At any time — to see what the system is doing.

## STEPS
1. Leads: `sqlite3 $LEADS_DB_PATH` — pipeline stats (total/relevant/in_progress/done/failed/converted).
2. Kanban (built-in): `hermes kanban list` or the dashboard `hermes dashboard` (http://127.0.0.1:9119) — active sprints and tasks by the naming `hab-<tweetid>-s<sprint>-<role>-<seq>`. Task run: `hermes kanban runs <task_id>`.
3. Docker: `docker ps` — which stacks are up (there should be none stuck after finished sprints).
4. MinIO: artifacts `hermes-artifacts/`, reports `hermes-reports/` (knowledge accumulating across days).
5. Profiles: statuses of subagents/delegations.

## OUTPUT
- A summary picture: which stage each lead is at, which sprints are active, what's been sold.

## NEXT
- Anomaly (a stuck stack, an expired token) → `l0-incident`. Integrity check → `l0-healthcheck`.

## LIMITS
- Observation only; do not interfere with an active sprint unless necessary.
