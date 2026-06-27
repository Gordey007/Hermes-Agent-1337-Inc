---
name: rs-handoff-architect
description: Finalize research/ + _notes.md and hand off to the architect via handoff.
version: 1.0.0
author: hermes-team
license: MIT
metadata:
  hermes:
    requires_toolsets: [sqlite, python]
---

# rs-handoff-architect

## WHO
researcher.

## WHEN
- `rs-decide-enough` returned "enough" or the github_search=10 limit was reached.

## STEPS
1. Check integrity: all `research/<NN>_*.md` artifacts have Title/URL/Sub-links/Summary/Cleaned; `_notes.md` is complete.
2. Build a short index for the architect: a list of `useful` artifacts + a one-line digest for each + gaps (if any).
3. `handoff` → architect role: mark the research task `review`/`done`, point to the input `research/`.

## OUTPUT
- A finished `research/` directory + `_notes.md`, handed off to the architect via kanban.

## NEXT
- The architect (`ar-read-research`) picks it up. The researcher is free (can answer `request-reply` ≤5).

## LIMITS
- I don't design or code — I only hand off references. After the handoff I edit research only on the architect's request (≤5).
