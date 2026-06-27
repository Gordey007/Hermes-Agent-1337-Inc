---
name: ev-verdict
description: Render the sprint verdict — keep / rollback / next-iteration / stop.
version: 1.0.0
author: hermes-team
license: MIT
metadata:
  hermes:
    requires_toolsets: [sqlite, python]
---

# ev-verdict

## WHO
evaluator.

## WHEN
- score + feedback are received (`ev-score-dod`).

## STEPS
1. Compare the score against the DoD threshold (all required checks passed → the goal is achieved).
2. Pick a verdict:
   - **keep** — the DoD is achieved, we lock in the result.
   - **rollback** — the last iteration made the metric worse → roll back to the previous state.
   - **next-iteration** — partial, there is progress and a clear gap, the limits are not exhausted.
   - **stop** — the limits (outer ≤10 / 5/5/10 iterations) are exhausted or there is no progress.
3. Record the verdict + a brief rationale in the eval task's kanban field.

## OUTPUT
- The verdict keep/rollback/next-iteration/stop + rationale (kanban).

## NEXT
- `ev-final-report` (we always write the report), then orchestrator_sprint (`os-decide-next`) executes the verdict.

## LIMITS
- One verdict. next-iteration is forbidden when the limits are exhausted (then stop). I do not edit code.
