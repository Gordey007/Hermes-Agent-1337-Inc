---
name: escalate
description: Escalation on limit overrun/blocker — hand the problem to the orchestrator with a reason.
version: 1.0.0
author: hermes-team
license: MIT
metadata:
  hermes:
    requires_tools: [kanban_block]
    requires_toolsets: [python]
---

# escalate

## WHO
Any profile facing a blocker or hitting the iteration limit.

## WHEN
- The counter reached its limit (5/5/10/10), the stack won't come up, no access, a contentious situation.

## STEPS
1. `kanban_block(<my_task_id>, reason="<which limit/blocker, what you tried, what's needed to unblock>")` — moves the task to `Blocked` and escalates to the human/orchestrator. For code under review, use the `review-required:` prefix in the reason.
2. The reason — 1–3 lines, specific. Do not duplicate content; give the path to the artifact.
3. The parent orchestrator (via `kanban.orchestrator_profile`) gets the parent task and decides what's next.

## OUTPUT
- The task in `blocked` status + a reason — visible to the orchestrator and the user during monitoring.

## NEXT
- The orchestrator decides: redirect / rollback / stop. When the outer loop is exhausted → sprint `failed` + evaluator report.

## LIMITS
- Do not loop: after escalating, do not continue the same operation without the orchestrator's decision.
