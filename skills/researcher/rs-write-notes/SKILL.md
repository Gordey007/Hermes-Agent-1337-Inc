---
name: rs-write-notes
description: Fill in research/_notes.md — for each artifact, useful/skip + why.
version: 1.0.0
author: hermes-team
license: MIT
metadata:
  hermes:
    requires_toolsets: [python]
---

# rs-write-notes

## WHO
researcher.

## WHEN
- After each new artifact in `research/`.

## STEPS
1. Rebuild the usefulness map from the artifacts:
   `python skills/tools/research_index/build_index.py --out "<research_dir>"`.
   It scans `research/*.md`, writes `research/_notes.md` (one `useful`/`skip` block per artifact,
   with heuristic prefill) + `research/_index.json` (machine index + unfollowed `next_hops`),
   and prints `{artifacts,useful,skip,next_hops}`.
2. Open `research/_notes.md` and CONFIRM or OVERRIDE each prefilled verdict against the DoD —
   flip `useful`↔`skip` and fix the `Why:` line where the heuristic was wrong.
3. The `Next hops` block lists unfollowed sub-links: feed promising ones back into
   `rs-github-search` / `rs-web-docs`.

## OUTPUT
- Updated `research/_notes.md` (confirmed useful/skip verdicts) + `research/_index.json`.

## NEXT
- `rs-decide-enough` (whether there are enough references).

## LIMITS
- Every artifact must get a useful/skip verdict. `_notes.md` is a compact map, not a content duplicate.
