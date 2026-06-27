---
name: dv-scaffold
description: Create product/ + docker-compose following the naming convention.
version: 1.0.0
author: hermes-team
license: MIT
metadata:
  hermes:
    requires_toolsets: [shell, python, docker]
---

# dv-scaffold

## WHO
developer.

## WHEN
- The build plan is ready (`dv-read-spec`).

## STEPS
1. `naming`: `docker_project=hab_<tweetid>_s<sprint>`, containers `hab_<tweetid>_s<sprint>_<component>`.
2. Create the `product/<component>/` structure for each component.
3. From the template `03_auto_research/docker-compose.tmpl.yml`, build `infra/compose/hab_<tweetid>_s<sprint>.yml`
   (services per component, sandbox-runner network, no public ports exposed externally).

## OUTPUT
- `product/` skeleton + compose config following the naming convention.

## NEXT
- `dv-spawn-subagent` for the first component.

## LIMITS
- Names strictly via `naming.py`. Isolation: the stack is brought up through `docker-sandbox` and is not published externally.
