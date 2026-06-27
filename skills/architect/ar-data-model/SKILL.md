---
name: ar-data-model
description: Write design/data-model.md (tables/fields/types/relations).
version: 1.0.0
author: hermes-team
license: MIT
metadata:
  hermes:
    requires_toolsets: [python]
---

# ar-data-model

## WHO
architect.

## WHEN
- `design/system-design.md` is ready.

## STEPS
1. From the components, derive the entities and their fields (name, type, constraints, indexes).
2. Describe the relations between entities and the owner of each table (which component).
3. Write `design/data-model.md` — this is the source of truth for the end-to-end contract (field↔backend↔API↔UI).

## OUTPUT
- `design/data-model.md`.

## NEXT
- `ar-api-contract`.

## LIMITS
- Field names are fixed here and from then on are not changed arbitrarily (end-to-end contract). A minimally sufficient model.
