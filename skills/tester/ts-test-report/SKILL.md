---
name: ts-test-report
description: Write reports/test_<seq>.md — what passed/failed, which tests are still needed, coverage.
version: 1.0.0
author: hermes-team
license: MIT
metadata:
  hermes:
    requires_toolsets: [python]
---

# ts-test-report

## WHO
tester.

## WHEN
- The unit run + DoD run are done.

## STEPS
1. Create `reports/test_<seq>.md` (seq via `naming.py`).
2. Record: unit pass/fail per component + failure logs; DoD per-check + weighted score; coverage; which tests are still needed.
3. Explicitly flag blockers (what prevents acceptance) — for the evaluator.

## OUTPUT
- `reports/test_<seq>.md` (survives the sprint — in `reports/`).

## NEXT
- `ts-handoff-evaluator`.

## LIMITS
- Facts of the runs only, no keep/rollback/stop verdict (that is the evaluator). I write into `reports/`.
