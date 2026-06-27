---
name: dv-spawn-subagent
description: Use subagent-spawn to bring up a role subagent (pack the spec into goal+context).
version: 1.0.0
author: hermes-team
license: MIT
metadata:
  hermes:
    requires_toolsets: [python]
    requires_tools: [delegate_task]
---

# dv-spawn-subagent

## WHO
developer (orchestrator over role subagents).

## WHEN
- The skeleton is ready; there is a component without an implementation.

## STEPS
1. Pick the component role from `design/component-<c>.md`: ml/backend/django/frontend.
2. `subagent-spawn` → `delegate_task(role="leaf")`. Pack the `context` COMPLETELY: `component-<c>.md`,
   the relevant data-model fields, the api-contract endpoints, the `product/<component>/` path, the container, and which `dv-role-*` to use.
3. Register the component in the contract checklist; increment `inner_loop` on each iteration.

## OUTPUT
- A running role subagent writing into `product/<component>/`.

## NEXT
- The remaining components in parallel/sequence → then `dv-component-contract`.

## LIMITS
- max_concurrent_children:3, max_spawn_depth:2, inner_loop ≤10/component. The subagent gets a CLEAN context — pack everything it needs.
