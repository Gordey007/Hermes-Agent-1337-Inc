---
name: dv-role-frontend-nextjs
description: Role instructions — frontend in Next.js/TypeScript.
version: 1.0.0
author: hermes-team
license: MIT
metadata:
  hermes:
    requires_toolsets: [shell, docker]
---

# dv-role-frontend-nextjs

## WHO
frontend role subagent (Next.js/TypeScript), spawned by the developer.

## WHEN
- A `component-<c>.md` with the frontend role arrived in `context`.

## STEPS
1. Create a Next.js/TS app in `product/<component>/`; the UI displays/sends exactly the fields in `data-model.md`.
2. API calls strictly per `api-contract.md` (paths/methods/schemas); the backend service base URL comes from the compose network.
3. Container `hab_<tweetid>_s<sprint>_<component>`; a page/route for the DoD (kind=http/contains).
4. Run in the sandbox (`build`/`start`), fix until the inner criteria pass.

## OUTPUT
- A working frontend in `product/<component>/` + a service in compose.

## NEXT
- Return the component status to the developer.

## LIMITS
- TypeScript ONLY for the frontend (everything else is Python). Fields/endpoints = the contract. inner_loop ≤10. Do not touch `dod_eval.py`.
