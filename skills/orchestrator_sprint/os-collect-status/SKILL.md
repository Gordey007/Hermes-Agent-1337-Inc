---
name: os-collect-status
description: Via collect-picture, poll researcher/architect/developer/tester.
version: 1.0.0
author: hermes-team
license: MIT
metadata:
  hermes:
    requires_toolsets: [sqlite, python]
---

# os-collect-status

## WHO
orchestrator_sprint.

## WHEN
- A phase has finished (the profile did a `handoff`) or a summary is needed before a decision.

## STEPS
1. `collect-picture`: poll the phase profiles — what was done, what wasn't, what was planned, which tests failed, what else is needed.
2. Cross-check against the phase's expected OUTPUT (artifacts in `research/`/`design/`/`product/`/`reports/`).
3. Record the summary in the sprint's root kanban task.

## OUTPUT
- A consolidated picture of the phase in kanban (readiness for the next phase or for a verdict).

## NEXT
- Phase is OK → `os-delegate-phase` for the next one. All phases done → `os-decide-next` (after the evaluator).

## LIMITS
- Gathering the picture only; I do not do the profiles' work. I trust the artifacts in the directory and don't re-ask without need.
