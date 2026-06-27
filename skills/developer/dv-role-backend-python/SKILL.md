---
name: dv-role-backend-python
description: Role instructions — backend in Python (API service).
version: 1.0.0
author: hermes-team
license: MIT
metadata:
  hermes:
    requires_toolsets: [shell, python, docker]
---

# dv-role-backend-python

## WHO
backend role subagent (Python), spawned by the developer.

## WHEN
- A `component-<c>.md` with the backend role arrived in `context`.

## STEPS
1. Implement the endpoints strictly per `api-contract.md` (methods/paths/schemas/error codes).
2. Data models = the fields in `data-model.md` (names must match). Wire up the storage from system-design.
3. Container `hab_<tweetid>_s<sprint>_<component>`; health endpoint for the DoD (kind=http).
4. Run in the sandbox, fix until the inner criteria pass.

## OUTPUT
- A working backend in `product/<component>/` + a service in compose.

## NEXT
- Return the status to the developer (ready / spec needs a fix).

## LIMITS
- The contract is fixed (fields/endpoints). Only your own component. inner_loop ≤10. Do not touch `dod_eval.py`.
