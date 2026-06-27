---
name: ev-collect-picture
description: Use collect-picture to poll developer/architect/tester — the full sprint picture.
version: 1.0.0
author: hermes-team
license: MIT
metadata:
  hermes:
    requires_toolsets: [sqlite, python]
---

# ev-collect-picture

## WHO
evaluator.

## WHEN
- tester did a `handoff` (test task is `done`).

## STEPS
1. `collect-picture`: poll developer/architect/tester — what was done, what was not, what was planned, which tests failed, what else was needed.
2. Read `reports/test_*.md`, `design/dod.md`, the state of `product/`.
3. Combine into a single picture: achieved vs target (DoD), known gaps, reasons for the failures.

## OUTPUT
- The full sprint picture (an internal note for the evaluation).

## NEXT
- `ev-score-dod`.

## LIMITS
- Collection and interpretation only. I do not edit code. I rely on the tester's reports and do not re-run the units myself.
