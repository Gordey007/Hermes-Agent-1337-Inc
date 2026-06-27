---
name: handoff
description: A handoff protocol between profiles — pack the artifact into kanban and mark it "ready to receive".
version: 1.0.0
author: hermes-team
license: MIT
metadata:
  hermes:
    requires_tools: [kanban_complete, kanban_create]
    requires_toolsets: [python]
---

# handoff

## WHO
Any profile that has finished a phase: researcher→architect, architect→developer, developer→tester, tester→evaluator.

## WHEN
- Your work is ready (the artifact is in the sprint's shared directory), task status → review/done.

## STEPS
1. Make sure the output artifact is in place per the naming convention (`research/`/`design/`/`product/`/`reports/`).
2. Finish your task with a structured handoff: `kanban_complete(<my_task_id>, summary="<1 line>", metadata={"artifact": "<path>", "handoff_to": "<next_profile>"})`.
3. Create a task for the receiving profile: `kanban_create(title="hab-<tweetid>-s<N>-<next_role>-01", assignee="<next_profile>", tenant="hab_<tweetid>", body="input: <artifact path>")` (the dispatcher `hermes gateway` will pick it up by `assignee`).

## OUTPUT
- In kanban: my task `Done` (summary+metadata.artifact+handoff_to) + a created task for the receiving profile.

## NEXT
- The receiving profile reads the handoff via `kanban_show` (summary+metadata) and starts its phase.

## LIMITS
- Pass only the path + summary (do not duplicate content in kanban). One handoff — to one profile.
