---
name: docker-sandbox
description: Bring up/tear down an isolated docker-compose sprint stack by naming convention (down -v).
version: 1.0.0
author: hermes-team
license: MIT
metadata:
  hermes:
    requires_toolsets: [docker, shell]
---

# docker-sandbox

## WHO
developer (build/run), tester (run), orchestrator_sprint/evaluator (teardown).

## WHEN
- developer: bring up the stack for the inner loop. tester: bring it up for a run. evaluator: tear it down during cleanup.

## STEPS
Project per `naming.py`: `hab_<tweetid>_s<sprint>`. Template: `03_auto_research/docker-compose.tmpl.yml`
→ materialized into `infra/compose/hab_<tweetid>_s<sprint>.yml`.

1. Generate the compose from the template (substitute `${TWEETID} ${SPRINT} ${WORKDIR}`).
2. Bring up: `docker compose -p hab_<tweetid>_s<sprint> -f <compose> up -d --build`.
   Isolated network `hab_net_<tweetid>_<sprint>`, `restart: "no"`.
3. Check: `docker compose -p hab_<tweetid>_s<sprint> ps`; logs `... logs <component>`.
4. Tear down (teardown): `docker compose -p hab_<tweetid>_s<sprint> down -v` (removes volumes).

## OUTPUT
- Running containers `hab_<tweetid>_s<sprint>_<component>` on an isolated network.
- After teardown — `docker ps -a` is empty for this project.

## NEXT
- Brought up → developer/tester work. Torn down → evaluator continues with `ev-cleanup` (drop-all-except-reports).

## LIMITS
- Only your own project `-p`. Never touch other stacks / global containers. Always `down -v` (do not leave volumes behind).
