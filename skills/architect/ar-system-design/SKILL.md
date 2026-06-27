---
name: ar-system-design
description: Write design/system-design.md (components, flows, stack).
version: 1.0.0
author: hermes-team
license: MIT
metadata:
  hermes:
    requires_toolsets: [python]
---

# ar-system-design

## WHO
architect.

## WHEN
- `ar-read-research` produced a digest of references.

## STEPS
1. Define the product's components (backend/ML/frontend), their responsibilities and boundaries.
2. Describe the data flows between components and external dependencies (containers per the naming `hab_<tweetid>_s<sprint>_<component>`).
3. Fix the stack: Python for backend/ML/Django, Next.js/TypeScript for the frontend.
4. Write `design/system-design.md` (components, flow diagram, stack, rationale from the references).

## OUTPUT
- `design/system-design.md`.

## NEXT
- `ar-data-model`.

## LIMITS
- I design for the achievable minimum that satisfies the DoD. I don't code. I rely on useful references.
