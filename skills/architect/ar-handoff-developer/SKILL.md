---
name: ar-handoff-developer
description: Hand out goals to the developer (one per component) via handoff.
version: 1.0.0
author: hermes-team
license: MIT
metadata:
  hermes:
    requires_toolsets: [sqlite, python]
---

# ar-handoff-developer

## WHO
architect.

## WHEN
- `design/` is complete: system-design, data-model, api-contract, component-*, dod.md.

## STEPS
1. Check the contract's consistency (data-model fields = api schemas = component-spec fields).
2. Build an index for the developer: a list of components + a link to each one's `design/component-<c>.md`.
3. `handoff` → developer role: design task `done`, point to the input `design/`.

## OUTPUT
- The `design/` set handed to the developer + the list of components in kanban.

## NEXT
- The developer (`dv-read-spec`) picks it up. The architect answers the developer's `request-reply` (≤5).

## LIMITS
- I don't code. After the handoff I edit `design/` only on the developer's request (≤5) or on `og-refine-dod`.
