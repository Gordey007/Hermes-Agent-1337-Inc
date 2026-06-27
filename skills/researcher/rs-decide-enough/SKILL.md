---
name: rs-decide-enough
description: Decide whether there are enough references; if not, refine and repeat (≤10).
version: 1.0.0
author: hermes-team
license: MIT
metadata:
  hermes:
    requires_toolsets: [python]
---

# rs-decide-enough

## WHO
researcher.

## WHEN
- After each new artifact + entry in `_notes.md`.

## STEPS
1. Compare the accumulated `useful` references against the topics in `research/_plan.md` and the DoD checks.
2. If every key topic is covered by at least one useful reference → enough.
3. If there's a gap AND `github_search` < 10 → form the next query (dig into `sub_links` via `fetch-clean` or a new `search-*`).

## OUTPUT
- A decision: "enough" or "next query: <what to search for>".

## NEXT
- Enough → `rs-handoff-architect`. Otherwise → `rs-github-search`/`rs-web-docs`.

## LIMITS
- Hard stop at `github_search`=10 (even if gaps remain) → still `rs-handoff-architect` with a note about the gap.
