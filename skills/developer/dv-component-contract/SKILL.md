---
name: dv-component-contract
description: Verify end-to-end consistency (table fields↔backend↔API↔UI).
version: 1.0.0
author: hermes-team
license: MIT
metadata:
  hermes:
    requires_toolsets: [python]
---

# dv-component-contract

## WHO
developer.

## WHEN
- Several components are ready (subagents returned their status).

## STEPS
1. Take the contract checklist from `dv-read-spec` (data-model fields).
2. Verify along the chain: a field in the table → backend model → api-contract schema → usage in the UI. Names and types must match.
3. On a mismatch → return it precisely to the right subagent (`dv-spawn-subagent`/fix) OR, if the error is in the spec, `dv-request-architect` (≤5).

## OUTPUT
- A contract consistency report (green / list of mismatches) in the kanban.

## NEXT
- Contract green → `dv-integrate`. Otherwise → fixes.

## LIMITS
- I do not change field names myself — that is the spec. A mismatch caused by the spec → architect (≤5). dev_architect ≤5.
