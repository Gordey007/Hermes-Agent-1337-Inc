---
name: dv-role-django-python
description: Role instructions — Django service in Python.
version: 1.0.0
author: hermes-team
license: MIT
metadata:
  hermes:
    requires_toolsets: [shell, python, docker]
---

# dv-role-django-python

## WHO
Django role subagent (Python), spawned by the developer.

## WHEN
- A `component-<c>.md` with the django role arrived in `context`.

## STEPS
1. Create a Django project/app in `product/<component>/`; models = the fields in `data-model.md` (names must match).
2. Views/URLs = the endpoints in `api-contract.md`; migrations are applied at container startup.
3. Container `hab_<tweetid>_s<sprint>_<component>`; health endpoint for the DoD (kind=http).
4. Run in the sandbox (`manage.py migrate`/`runserver`/`check`), fix until the inner criteria pass.

## OUTPUT
- A working Django service in `product/<component>/` + a service in compose.

## NEXT
- Return the component status to the developer.

## LIMITS
- The contract is fixed (models/URLs). Only your own component. inner_loop ≤10. Do not touch `dod_eval.py`.
