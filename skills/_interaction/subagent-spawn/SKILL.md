---
name: subagent-spawn
description: Spawn a subagent via delegate_task — pack everything into goal+context (clean context).
version: 1.0.0
author: hermes-team
license: MIT
metadata:
  hermes:
    requires_toolsets: [python]
    requires_tools: [delegate_task]
---

# subagent-spawn

## WHO
Orchestrators (orchestrator_sprint delegates phases) and developer (spawns role-* workers per component).

## WHEN
- You need to run a profile/role on a separate task. The subagent gets a CLEAN context — pack everything needed
  into `goal` and `context`.

## STEPS
1. Form the `goal` — one clear objective (what the result should be, which DoD/criterion).
2. Form the `context` — everything the subagent does not know: paths to artifacts (`design/`, `research/`),
   naming (tweet_id/sprint/component), iteration limits, which profile/role and which skill to apply.
3. `delegate_task(goal=..., context=..., role="leaf"|"orchestrator", profile=<name>)`.
4. Record the subagent's task in kanban (`naming.py` id), status `in_progress`.
5. Wait for the result (artifact in the shared directory + handoff), read it via `kanban-read`.

## OUTPUT
- A spawned subagent + a kanban task; on completion — an artifact in the sprint's shared directory.

## NEXT
- developer: after all components → `dv-component-contract` + `dv-integrate`.
- orchestrator_sprint: after a phase → `os-collect-status` / `os-decide-next`.

## LIMITS
- `max_spawn_depth: 2`, `max_concurrent_children: 3`. Exceeding → `escalate`. Do not duplicate context — give only the minimum needed.
