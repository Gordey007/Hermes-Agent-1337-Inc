---
name: ts-read-dod
description: Read design/dod.md + spec, derive what to check.
version: 1.0.0
author: hermes-team
license: MIT
metadata:
  hermes:
    requires_toolsets: [python]
---

# ts-read-dod

## WHO
tester.

## WHEN
- developer did a `handoff` (dev task is `done`/`review`).

## STEPS
1. Read `design/dod.json`/`dod.md` (machine checks: http/file_exists/contains/cmd + weight) and the "component↔DoD-check" map.
2. Read `api-contract.md` for negative/edge cases.
3. Produce a check plan: per-component unit tests + a DoD run.

## OUTPUT
- A testing plan (what and how we check) in an internal note.

## NEXT
- `ts-author-unit-tests`.

## LIMITS
- I do not edit code or change `dod_eval.py`/`dod.json`. I check strictly against the contract.
