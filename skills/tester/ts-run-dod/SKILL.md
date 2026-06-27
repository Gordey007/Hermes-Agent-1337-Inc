---
name: ts-run-dod
description: Run the DoD check (dod_eval from 03).
version: 1.0.0
author: hermes-team
license: MIT
metadata:
  hermes:
    requires_toolsets: [shell, python, docker]
---

# ts-run-dod

## WHO
tester.

## WHEN
- The unit run is done (`ts-run-tests`), the stack is up.

## STEPS
1. Run the immutable evaluator: `python 03_auto_research/dod_eval.py --dod design/dod.json --project hab_<tweetid>_s<sprint>`.
2. For each check (http/file_exists/contains/cmd), collect: passed/failed + weight + the actual result.
3. Compute the total weighted score and the list of failed checks.

## OUTPUT
- DoD result: per-check pass/fail + weighted score (machine + human-readable).

## NEXT
- `ts-test-report`.

## LIMITS
- Do NOT modify `dod_eval.py` or `dod.json` (immutable input). I only run it and collect the result. The verdict belongs to the evaluator.
