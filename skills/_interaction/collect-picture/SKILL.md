---
name: collect-picture
description: Poll several profiles and assemble a full picture of the sprint (done/not done/tests/plans).
version: 1.0.0
author: hermes-team
license: MIT
metadata:
  hermes:
    requires_tools: [kanban_list, kanban_show]
    requires_toolsets: [python]
---

# collect-picture

## WHO
evaluator and orchestrator_sprint.

## WHEN
- Before the verdict (evaluator) or before deciding on the next phase (orchestrator_sprint).

## STEPS
1. `kanban_list(tenant="hab_<tweetid>")` — collect all sprint tasks and their statuses.
2. For each profile (researcher/architect/developer/tester), via `kanban_show(<task_id>)` read the summary+metadata (artifact path) and the output artifact itself.
3. Summarize: what's done / what's NOT done / what was planned / which tests failed / what's still missing.
4. Cross-check against the counters: `python 04_team/kanban/counters.py list --tweet <tweetid> --sprint <N>` (where a limit was hit).

## OUTPUT
- A summary picture (structured text) — input for `ev-verdict` or `os-decide-next`.

## NEXT
- evaluator → `ev-score-dod` + `ev-verdict`. orchestrator_sprint → `os-decide-next`.

## LIMITS
- Read/aggregate only; do not edit other profiles' artifacts.
