---
name: dv-request-architect
description: Use request-reply to ask the architect about a gap/error in the spec (≤5).
version: 1.0.0
author: hermes-team
license: MIT
metadata:
  hermes:
    requires_toolsets: [sqlite, python]
---

# dv-request-architect

## WHO
developer.

## WHEN
- During the build a gap/contradiction is found in `design/` (the contract is unimplementable/incomplete).

## STEPS
1. Formulate a SPECIFIC request: which component, which spot in the spec, what does not add up, which option I propose.
2. `request-reply` → architect role: record it in the kanban, increment the `dev_architect` counter.
3. Wait for the updated `design/` (the architect calls the researcher if needed, ≤5), then continue the build.

## OUTPUT
- A request in the kanban + (per the reply) a clarified `design/`.

## NEXT
- Return to the interrupted dv-* skill.

## LIMITS
- `dev_architect` ≤5. Exceeding it → `escalate` to orchestrator_sprint. I do not edit the spec myself.
