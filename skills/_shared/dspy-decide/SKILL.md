---
name: dspy-decide
description: Make a pipeline judgement call (qualify lead, pick task, author/refine DoD, research-enough, verdict, offer, reply) via the optimized DSPy tool instead of an ad-hoc prompt.
version: 1.0.0
author: hermes-team
license: MIT
metadata:
  hermes:
    requires_toolsets: [python]
---

# dspy-decide

## WHO
Any profile at a decision point: orchestrator_global, researcher, evaluator, sales.

## WHEN
- You must make one of the registered judgement calls (see table). Do NOT hand-write a
  prompt for these — call the DSPy tool so the decision uses the optimized few-shot program.

| Decision | `--name` | Input JSON keys | Output keys |
|---|---|---|---|
| Qualify a lead | `qualify_lead` | `tweet_text` | `is_relevant`, `intent`, `reason` |
| Pick simplest lead | `pick_simplest_task` | `candidates` (JSON list) | `chosen_tweet_id`, `justification` |
| Author DoD from lead | `author_dod` | `tweet_text`, `design_notes` | `direction`, `dod_checks` |
| Refine DoD | `refine_dod` | `prev_dod`, `evaluator_report` | `refined_dod`, `changelog` |
| Research enough? | `research_enough` | `notes`, `found_count` | `enough`, `next_query` |
| Sprint verdict | `evaluator_verdict` | `dod_feedback`, `test_report`, `iteration` | `verdict`, `rationale` |
| Build offer | `build_offer` | `tweet_text`, `product_summary` | `offer_text` |
| Analyze reply | `analyze_reply` | `reply_text` | `sentiment`, `reply_status`, `summary` |

## STEPS
1. Build the input JSON with exactly the keys for your decision (table above).
2. Call the tool — it loads the compiled program if available, else zero-shot:
   ```bash
   echo '<input-json>' | uv run skills/tools/dspy/run.py --name <name>
   ```
   (or `--input '<json>'`). List programs with `uv run skills/tools/dspy/run.py --list`.
3. Read ONLY the JSON printed on stdout. Parse the output keys for the next action.

## OUTPUT
- A compact JSON object with the decision's output keys. Persist it where your role records
  decisions (kanban field, `leads` column, `dod.json`, `reports/`).

## NEXT
- `qualify_lead`/`pick_simplest_task` → orchestrator_global continues `og-*` flow.
- `author_dod`/`refine_dod` → write `program.md` / `dod.json` (still author-frozen for executors).
- `research_enough` → loop research or `rs-handoff-architect`.
- `evaluator_verdict` → `os-decide-next` (keep/rollback/next/stop).
- `build_offer`/`analyze_reply` → sales `sl-send-x` / update `reply_status`.

## LIMITS
- Needs `NVIDIA_API_KEY` + `uv sync --extra dspy`; tool prints a clear error otherwise.
- Never import dspy directly or write your own prompt for these decisions — always go through
  `run.py` so improvements from nightly optimization apply automatically.
- Inputs are text-only; do not pass secrets or full file contents — pass summaries.
