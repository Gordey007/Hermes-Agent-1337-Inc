---
name: kanban-write
description: Create/link/close/block a kanban task and increment the iteration counter via the built-in Hermes kanban.
version: 1.0.0
author: hermes-team
license: MIT
metadata:
  hermes:
    requires_tools: [kanban_create, kanban_link, kanban_comment, kanban_complete, kanban_block]
---

# kanban-write

## WHO
Any profile recording progress; decomposition and counters are managed by orchestrator_sprint and by executors on request.

## WHEN
- When decomposing a sprint, at the end of a phase (complete/block), on handoff, and on every request-reply request (counter +1).

## STEPS
Kanban is a built-in Hermes tool. Act via tool calls. Titles/assignee/tenant follow `infra/naming.py`.

1. Create a child task (decomposition):
   `kanban_create(title="hab-<tweetid>-s<sprint>-<role>-<seq>", assignee="<profile>", tenant="hab_<tweetid>", body="<goal + link to DoD/artifact>")`,
   then `kanban_link(parent=<root_task>, child=<new>)`. The dispatcher (`hermes gateway`) spawns the worker by `assignee`.
2. Note/progress in the thread: `kanban_comment(<task_id>, "<what was done/status>")`.
3. Finish your phase (success): `kanban_complete(<task_id>, summary="<result>", metadata={"artifact": "<path|minio-key>", "handoff_to": "<profile>"})`.
4. Block/escalate: `kanban_block(<task_id>, "<reason>")` (for code edits — prefix with `review-required:`).
5. Increment the iteration counter (kanban does not count natively):
   `python 04_team/kanban/counters.py inc --tweet <tweetid> --sprint <N> --counter <name>` → returns `{value, max, over_limit}`; mirror the value into `kanban_comment`.

## OUTPUT
- The updated task (status/comments/metadata) — visible to the human in the dashboard and via `hermes kanban show`.
- The sidecar counter is updated.

## NEXT
- `kanban_complete` → the dispatcher activates the next child / the orchestrator judges whether dependencies are complete.
- `kanban_block` or `over_limit=true` → `escalate` to orchestrator_sprint.

## LIMITS
- Before incrementing, check the limit (5/5/10/10): if reached → do not continue the action, instead `kanban_block`/`escalate`.
