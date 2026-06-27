# tools/dspy — DSPy as a tool for every profile

DSPy is used **everywhere a profile makes a judgement call**: qualify a lead, pick the
simplest task, author/refine the DoD, decide research is enough, the evaluator verdict, the
sales offer, reply analysis. Instead of hand-written prompts scattered across skills, each
decision is a typed **DSPy signature** that can be **optimized** (few-shot demos + tuned
instructions) and saved, then called through one CLI — exactly like the researcher's tools.

| File | What it is | Used by |
|---|---|---|
| `lm.py` | Wires DSPy to the NVIDIA endpoint: working LM (task) + reflection LM (optimizer) | all of the below |
| `signatures.py` | One typed `dspy.Signature` per decision point + a name→type registry | programs/optimize |
| `programs.py` | Builds Predict/ChainOfThought per signature; loads `compiled/<name>.json` if present | run/optimize |
| `optimize.py` | BootstrapFewShot / MIPROv2 / GEPA against a JSONL trainset → `compiled/<name>.json` | nightly cron, L0 |
| `run.py` | **The tool boundary**: run a program on JSON, print JSON (compiled if available, else zero-shot) | every skill |

## Decision points (programs)

| name | signature | module | who calls it |
|---|---|---|---|
| `qualify_lead` | is this a real, payable lead? | Predict | orchestrator_global (`og-qualify-lead`) |
| `pick_simplest_task` | which lead is simplest to ship? | ChainOfThought | orchestrator_global (`og-pick-task`) |
| `author_dod` | lead → program.md body + dod checks | ChainOfThought | orchestrator_global (`og-author-dod`) |
| `refine_dod` | tighten DoD from evaluator report | ChainOfThought | orchestrator_global (`og-refine-dod`) |
| `research_enough` | enough refs, or next query? | Predict | researcher (`rs-decide-enough`) |
| `evaluator_verdict` | keep / rollback / next / stop | ChainOfThought | evaluator (`ev-verdict`) |
| `build_offer` | personal, non-pushy offer | ChainOfThought | sales (`sl-build-offer`) |
| `analyze_reply` | sentiment + reply_status | Predict | sales (`sl-analyze-reply`) |

## How a skill uses it

```bash
echo '{"tweet_text":"I will pay for a tiny CSV→chart web tool"}' \
  | uv run skills/tools/dspy/run.py --name qualify_lead
# → {"is_relevant": true, "intent": "willing_to_pay", "reason": "..."}
```

The skill reads only the JSON output — no dspy import, no prompt text. The shared skill
`skills/_shared/dspy-decide/SKILL.md` documents this for every profile.

## Optimization (best practices applied)

```bash
# few-shot demos from traces (cheapest)
uv run skills/tools/dspy/optimize.py --name qualify_lead \
    --trainset data/qualify_lead.jsonl --optimizer bootstrap
# instructions + demos (medium data)         → --optimizer mipro
# reflective, feedback-aware (strongest)      → --optimizer gepa
```

- **Two LMs** (`lm.py`): a cheap working LM runs programs, a stronger reflection LM proposes
  better instructions during MIPRO/GEPA.
- **Model-agnostic**: swap `DSPY_WORKING_MODEL` / `DSPY_REFLECTION_MODEL` without touching code.
- **Save/load compiled programs**: `optimize.py` writes `compiled/<name>.json`; `run.py` loads
  it automatically — zero-shot until optimized, optimized after.
- **Nightly re-optimization**: L0 can cron `optimize.py` over accumulated `data/*.jsonl`
  (labels harvested from `leads` outcomes + evaluator reports) so the pipeline keeps improving.

## Trainset format (`data/<name>.jsonl`)

```json
{"inputs": {"tweet_text": "..."}, "label": {"is_relevant": true, "intent": "willing_to_pay"}}
```

## Environment

```bash
export NVIDIA_API_KEY="nvapi-..."             # required to call the model; see env.example
export DSPY_LM_BASE="https://integrate.api.nvidia.com/v1"
export DSPY_WORKING_MODEL="openai/nvidia/nemotron-4-340b-instruct"
export DSPY_REFLECTION_MODEL="openai/nvidia/llama-3.1-nemotron-70b-instruct"
export DSPY_COMPILED_DIR="skills/tools/dspy/compiled"   # default
uv sync --extra dspy                          # installs dspy-ai
```

`dspy` is an optional dependency: `run.py`/`optimize.py` raise a clear
"run `uv sync --extra dspy`" if it is missing, so the rest of the repo imports cleanly.
