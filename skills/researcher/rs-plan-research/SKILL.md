---
name: rs-plan-research
description: Derive from the DoD/task a list of what to search for (terms, stack, patterns).
version: 1.0.0
author: hermes-team
license: MIT
metadata:
  hermes:
    requires_toolsets: [python]
---

# rs-plan-research

## WHO
researcher.

## WHEN
- A research phase has been received (there is `design/dod.json` + the task text in `context`).

## STEPS
1. Read the task and the DoD. Identify the target stack (Python/Next.js), key entities, and patterns.
2. Build a list of search topics: reference repositories, specific files by code, sections of official documentation.
3. Prioritize: first the things that directly satisfy the DoD checks.

## OUTPUT
- `research/_plan.md`: an ordered list of topics/queries (what we're searching for and why).

## NEXT
- `rs-github-search` for the first item in the plan.

## LIMITS
- The plan is just a map; at most ≤10 GitHub queries per sprint. Do not dive into anything irrelevant to the DoD.
