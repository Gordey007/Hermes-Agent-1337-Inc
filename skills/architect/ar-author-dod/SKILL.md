---
name: ar-author-dod
description: Refine the acceptance criteria in design/dod.md, inheriting the DoD from orchestrator_global.
version: 1.0.0
author: hermes-team
license: MIT
metadata:
  hermes:
    requires_toolsets: [python]
---

# ar-author-dod

## WHO
architect.

## WHEN
- The per-component specs are ready; there is an initial `design/dod.json` v1 from orchestrator_global.

## STEPS
1. Read the initial `dod.json` (machine checks: http/file_exists/contains/cmd + weight).
2. Make it concrete for the designed system: bind each check to a real endpoint/file/command/container.
3. Write a human-readable `design/dod.md` (what is checked and how) + if needed refine `design/dod.json` (without weakening it).

## OUTPUT
- `design/dod.md` (+ an agreed `design/dod.json`), bound to the components.

## NEXT
- `ar-handoff-developer`.

## LIMITS
- The DoD stays machine-checkable and is not weakened without agreement from orchestrator_global. `dod_eval.py` is unchanged.
