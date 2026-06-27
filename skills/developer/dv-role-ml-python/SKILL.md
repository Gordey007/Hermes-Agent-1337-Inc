---
name: dv-role-ml-python
description: Role instructions — ML component in Python.
version: 1.0.0
author: hermes-team
license: MIT
metadata:
  hermes:
    requires_toolsets: [shell, python, docker]
---

# dv-role-ml-python

## WHO
ML role subagent (Python), spawned by the developer.

## WHEN
- A `component-<c>.md` with the ml role arrived in `context`.

## STEPS
1. Implement the ML logic (inference/processing) in `product/<component>/` in Python; dependencies in requirements.
2. Honor the interface from the contract: inputs/outputs = data-model fields, format = api-contract.
3. Wrap it in the container `hab_<tweetid>_s<sprint>_<component>`; provide a health endpoint/CLI for the DoD check.
4. Run it locally in the sandbox; fix until the component's inner criteria pass.

## OUTPUT
- A working ML component in `product/<component>/` + a service in compose.

## NEXT
- Return the component status to the developer (ready / spec needs a fix → the developer decides on `dv-request-architect`).

## LIMITS
- Only your own component. Do not change field/endpoint names (the contract). inner_loop ≤10. Do not edit `dod_eval.py`.
