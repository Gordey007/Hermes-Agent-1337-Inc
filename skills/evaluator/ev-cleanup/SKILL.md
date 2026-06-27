---
name: ev-cleanup
description: drop-all-except-reports — down -v, remove working directories, keep reports/.
version: 1.0.0
author: hermes-team
license: MIT
metadata:
  hermes:
    requires_toolsets: [shell, docker]
---

# ev-cleanup

## WHO
evaluator.

## WHEN
- `reports/final.md` is written (`ev-final-report`).

## STEPS
1. `docker-sandbox`: `docker compose -p hab_<tweetid>_s<sprint> down -v` (containers + volumes).
2. Check `docker ps -a` — no sprint containers remain.
3. Remove the sprint's working subdirectories EXCEPT `reports/`: `research/`, `design/`, `product/`.
4. Make sure `/sandbox/work/hab_<tweetid>/s<sprint>/reports/` is intact.

## OUTPUT
- A clean environment: only `reports/` remains.

## NEXT
- `ev-push-reports`.

## LIMITS
- NEVER delete `reports/` or the DBs (`leads`/`tasks`). Drop only the isolated sprint environment.
