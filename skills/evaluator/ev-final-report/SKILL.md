---
name: ev-final-report
description: Write reports/final.md — sprint outcome, working examples, recommendations.
version: 1.0.0
author: hermes-team
license: MIT
metadata:
  hermes:
    requires_toolsets: [python]
---

# ev-final-report

## WHO
evaluator.

## WHEN
- The verdict is rendered (`ev-verdict`).

## STEPS
1. Create `reports/final.md` with the structure:
   - **Verdict** — keep/rollback/next-iteration/stop + score.
   - **Done / Not done** — what worked, what did not (by DoD checks).
   - **Working examples** — working code/config snippets from `product/` (what definitely works).
   - **References** — which references from `research/_notes.md` worked, which did not.
   - **Recommendations** — what to clarify in the DoD/design for the next day (for `og-refine-dod`).
2. Rely on `reports/test_*.md`, the sprint picture, and the DSPy feedback.

## OUTPUT
- `reports/final.md` (survives the sprint).

## NEXT
- `ev-cleanup`.

## LIMITS
- I write only into `reports/`. I do not edit code/spec. Accumulating knowledge across days is the report's main value.
