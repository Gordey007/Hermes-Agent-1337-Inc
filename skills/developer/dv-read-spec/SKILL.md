---
name: dv-read-spec
description: Read design/ and produce a per-component build plan.
version: 1.0.0
author: hermes-team
license: MIT
metadata:
  hermes:
    requires_toolsets: [python]
---

# dv-read-spec

## WHO
developer.

## WHEN
- architect did a `handoff` (design task is `done`).

## STEPS
1. Read `design/system-design.md`, `data-model.md`, `api-contract.md`, all `component-*.md`, and `dod.md`.
2. Produce a build plan: component order, dependencies, which roles are needed (ml/backend/django/frontend).
3. Capture the end-to-end contract (fields↔API↔UI) as a checklist for `dv-component-contract`.

## OUTPUT
- Internal build plan + contract checklist.

## NEXT
- `dv-scaffold`.

## LIMITS
- Do not edit the spec. When details are missing → `dv-request-architect` (≤5). Do the minimum that satisfies the DoD.
