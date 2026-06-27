---
name: ts-handoff-evaluator
description: Hand off the testing results to the evaluator via handoff.
version: 1.0.0
author: hermes-team
license: MIT
metadata:
  hermes:
    requires_toolsets: [sqlite, python]
---

# ts-handoff-evaluator

## WHO
tester.

## WHEN
- `reports/test_<seq>.md` is ready.

## STEPS
1. Provide a link to `reports/test_<seq>.md` + the final DoD weighted score + the list of blockers.
2. `handoff` → evaluator role: test task `done`, input = `reports/test_*.md` + the stack up/down as needed.

## OUTPUT
- The testing results handed to the evaluator via the kanban.

## NEXT
- The evaluator (`ev-collect-picture`) picks it up.

## LIMITS
- I do not render a verdict. After the handoff I re-test only when returned (next-iteration) by orchestrator_sprint.
