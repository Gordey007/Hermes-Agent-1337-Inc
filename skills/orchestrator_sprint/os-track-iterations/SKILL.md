---
name: os-track-iterations
description: Maintain iteration counters and watch the limits (5/5/10/10).
version: 1.0.0
author: hermes-team
license: MIT
metadata:
  hermes:
    requires_tools: [kanban_comment]
    requires_toolsets: [python]
---

# os-track-iterations

## WHO
orchestrator_sprint.

## WHEN
- A phase with a request↔response cycle or inner-loop is in progress (dev/research/design).

## STEPS
1. Read the sidecar counters: `python 04_team/kanban/counters.py list --tweet <tweetid> --sprint <N>` (dev_architect, architect_researcher, github_search, inner_loop, outer_loop).
2. On each request/iteration, increment the corresponding one: `python 04_team/kanban/counters.py inc --tweet <tweetid> --sprint <N> --counter <name>` → mirror the value into the task thread (`kanban_comment`).
3. Compare against the limits (the `over_limit` field in the output): dev_architect≤5, architect_researcher≤5, github_search≤10, inner_loop≤10, outer_loop≤10.

## OUTPUT
- Up-to-date counters in the sidecar + visible to a human in the task comments.

## NEXT
- Within the limit → continue the phase. Exceeded → `escalate` + move the sprint to `os-decide-next` (likely stop/eval).

## LIMITS
- The limits are hard. Exceeding any of them = immediate stop of the phase and an evaluator report.
