---
name: ar-request-research
description: Request the researcher via request-reply when information is missing (≤5).
version: 1.0.0
author: hermes-team
license: MIT
metadata:
  hermes:
    requires_toolsets: [sqlite, python]
---

# ar-request-research

## WHO
architect.

## WHEN
- During design, a critical gap in the references is discovered.

## STEPS
1. Formulate a SPECIFIC request: what exactly needs to be found and why (for which decision/component).
2. `request-reply` → researcher role: record the request in kanban, increment the `architect_researcher` counter.
3. Wait for the reply (new/refined artifacts in `research/`), continue the design.

## OUTPUT
- A request in kanban + (upon reply) an augmented `research/`.

## NEXT
- Return to the interrupted ar-* skill (system-design/component-spec).

## LIMITS
- `architect_researcher` ≤5. Exceeding → `escalate` to orchestrator_sprint, design with what's available and note the gap.
