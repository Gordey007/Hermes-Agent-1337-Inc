---
name: l0-healthcheck
description: Integrity check — DB schema, docker with no stuck containers, MinIO, token validity.
version: 1.0.0
author: hermes-team
license: MIT
metadata:
  hermes:
    requires_toolsets: [shell, python, sqlite]
---

# l0-healthcheck

## WHO
The main Hermes agent (L0).

## WHEN
- After `l0-bootstrap`, periodically, before starting a new sprint.

## STEPS
1. DB: `sqlite3 $LEADS_DB_PATH "PRAGMA table_info(leads);"` — the `tweet_id` column must be present (Step 0).
   The built-in kanban is reachable: `hermes kanban list` and `hermes gateway status` (the dispatcher is alive).
2. Docker: `docker ps -a` — no stuck `hab_*` containers from finished sprints.
3. MinIO: the buckets `hermes-artifacts`/`hermes-reports` exist and are reachable.
4. Tokens: a trial call to GitHub (`gh_search`), Stripe (TEST), X — no 401/403; keys are valid.

## OUTPUT
- A health report: OK/problem for each item.

## NEXT
- All OK → the system is ready. Problem → `l0-incident`.

## LIMITS
- Do not perform destructive operations; checks only (read-only probes).
