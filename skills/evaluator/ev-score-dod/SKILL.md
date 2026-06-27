---
name: ev-score-dod
description: Run the DSPy metric against the DoD — numeric score + textual feedback.
version: 1.0.0
author: hermes-team
license: MIT
metadata:
  hermes:
    requires_toolsets: [shell, python]
---

# ev-score-dod

## WHO
evaluator.

## WHEN
- The full sprint picture is collected (`ev-collect-picture`).

## STEPS
1. Run the DSPy metric: `python 03_auto_research/dspy_eval.py --dod design/dod.json --report reports/test_*.md --project hab_<tweetid>_s<sprint>`.
2. Get a numeric score (0..1) + textual feedback (what drags it down, which checks failed, why).
3. Cross-reference with the check weights from `dod.json` and the blockers from `reports/test_*.md`.

## OUTPUT
- score + textual feedback (input for the verdict).

## NEXT
- `ev-verdict`.

## LIMITS
- I do not modify `dod_eval.py`/`dod.json`/`dspy_eval.py`. Running and interpreting only.
