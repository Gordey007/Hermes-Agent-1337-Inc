---
name: os-decide-next
description: Based on the evaluator's verdict, choose keep / rollback / next-iteration / stop.
version: 1.0.0
author: hermes-team
license: MIT
metadata:
  hermes:
    requires_toolsets: [sqlite, python]
---

# os-decide-next

## WHO
orchestrator_sprint.

## WHEN
- The evaluator has issued a verdict (`reports/final.md` is ready).

## STEPS
1. Read the evaluator's verdict: keep / rollback / next-iteration / stop.
2. `keep` → sprint `done`, move the root task to `done`.
3. `rollback` → roll the product back to the last "green" state; if there is inner-loop budget, repeat dev.
4. `next-iteration` → if outer-loop < 10 → notify global for `og-refine-dod` + restart; otherwise `stop`.
5. `stop` → sprint `failed`.

## OUTPUT
- Updated status of the sprint's root task + the decision recorded in kanban.

## NEXT
- `done`/`failed` → `os-teardown`. `next-iteration`/`rollback` → the corresponding phase/restart.

## LIMITS
- The decision relies ONLY on the evaluator's verdict + limits. I do not re-evaluate myself. outer-loop ≤10.
