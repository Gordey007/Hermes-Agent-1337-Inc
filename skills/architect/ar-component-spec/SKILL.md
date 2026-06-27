---
name: ar-component-spec
description: Per-component instructions (spec coding) for each developer role.
version: 1.0.0
author: hermes-team
license: MIT
metadata:
  hermes:
    requires_toolsets: [python]
---

# ar-component-spec

## WHO
architect.

## WHEN
- system-design + data-model + api-contract are ready.

## STEPS
1. For each component (`<component>`), write `design/component-<component>.md`: the role (ml/backend/django/frontend),
   what to implement, which fields/endpoints from the contract it owns/consumes, inputs/outputs, the component's done criteria.
2. Specify the container per the naming (`hab_<tweetid>_s<sprint>_<component>`) and its dependencies.
3. Reference the specific useful references from `research/`.

## OUTPUT
- A set of `design/component-*.md` (one per component).

## NEXT
- `ar-author-dod` (clarify the acceptance criteria) → then `ar-handoff-developer`.

## LIMITS
- The spec determines development (the developer does not invent architecture). Field/endpoint names come from the contract.
