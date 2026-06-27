---
name: ar-read-research
description: Read research/_notes.md, take only the useful references.
version: 1.0.0
author: hermes-team
license: MIT
metadata:
  hermes:
    requires_toolsets: [python]
---

# ar-read-research

## WHO
architect.

## WHEN
- The researcher did a `handoff` (research task `done`).

## STEPS
1. Open `research/_notes.md`, select the `useful` lines (ignore `skip`).
2. For each useful entry, open its artifact, read the Summary + the relevant Cleaned fragment.
3. Write the applicable patterns/stack/decisions into a working note.

## OUTPUT
- A short digest of the applicable references (an internal note for design).

## NEXT
- `ar-system-design`. If there's a critical gap → `ar-request-research`.

## LIMITS
- I don't read `skip` artifacts. I don't search myself — for a new search I call the researcher (≤5).
