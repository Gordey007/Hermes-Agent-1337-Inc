---
name: dv-integrate
description: Assemble the components together, bring up the stack, smoke-check.
version: 1.0.0
author: hermes-team
license: MIT
metadata:
  hermes:
    requires_toolsets: [shell, python, docker]
---

# dv-integrate

## WHO
developer.

## WHEN
- The end-to-end contract is green (`dv-component-contract`).

## STEPS
1. `docker-sandbox`: bring up the whole stack `docker compose -p hab_<tweetid>_s<sprint> up -d --build`.
2. Smoke-check the inter-component links: frontend→backend→storage/ML, health endpoints respond.
3. On an integration failure → a precise component fix (inner_loop) until the smoke is green.

## OUTPUT
- An integrated stack that is up and passed smoke; ready for testing.

## NEXT
- `dv-handoff-tester`.

## LIMITS
- inner_loop ≤10. If the smoke does not converge because of the contract → `dv-request-architect` (≤5). The tester runs the DoD, not me.
