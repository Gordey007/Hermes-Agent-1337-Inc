---
name: og-refine-dod
description: After the 1st iteration of the inner loop, refine the DoD based on the evaluator's report (versioning).
version: 1.0.0
author: hermes-team
license: MIT
metadata:
  hermes:
    requires_toolsets: [python]
---

# og-refine-dod

## WHO
orchestrator_global.

## WHEN
- The sprint finished its 1st iteration with a `next-iteration` verdict (the DoD turned out to be unachievable/incomplete).

## STEPS
1. Read `reports/final.md` (or `reports/test_*.md`) from the latest iteration.
2. Identify: what turned out to be unachievable, what is incomplete/ambiguous, what is over-engineered.
3. Adjust the `checks` in `dod.json` (drop unrealistic ones, clarify wording, fix `weight`).
4. Write a new version (`v<N+1>`) into `design/dod.md` + `design/dod.json` without overwriting history.

## OUTPUT
- `dod.json`/`dod.md` version v<N+1> + a brief note on "what changed and why".

## NEXT
- `og-start-sprint` (restart the sprint with the refined DoD) OR `og-close-day` (if the outer-loop limit is exhausted).

## LIMITS
- The DoD stays machine-verifiable. Do not exceed outer-loop ≤10. Do not simplify to the point of meaninglessness — otherwise `og-close-day`.
