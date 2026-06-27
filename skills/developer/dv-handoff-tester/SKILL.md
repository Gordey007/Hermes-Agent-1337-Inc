---
name: dv-handoff-tester
description: Hand off the assembled stack to the tester via handoff.
version: 1.0.0
author: hermes-team
license: MIT
metadata:
  hermes:
    requires_toolsets: [sqlite, python]
---

# dv-handoff-tester

## WHO
developer.

## WHEN
- Integration passed smoke (`dv-integrate`).

## STEPS
1. Capture the state: which components are assembled, how to bring up the stack (`-p hab_<tweetid>_s<sprint>`), which health endpoints exist.
2. Note the mapping of components to DoD checks (what is covered by what).
3. `handoff` → tester role: dev task `done`/`review`, input = `product/` + `design/dod.md`.

## OUTPUT
- The assembled stack handed to the tester + a "component↔DoD-check" map.

## NEXT
- The tester (`ts-read-dod`) picks it up. The developer responds to fixes only when returned via orchestrator_sprint.

## LIMITS
- I do not write tests or render a verdict. After the handoff I edit code only by orchestrator_sprint's decision (rollback/next-iteration).
