# 03 — Evaluation (DoD + DSPy/GEPA)

## DoD (Definition of Done)
The "product is ready" criteria in two forms:
- **`dod.json`** — machine-readable checks: `{"checks":[{"id","kind","weight"}]}`, where `kind` ∈ `http` / `file_exists` / `contains` / `cmd`.
- **`dod.md`** — a human-readable description of the same criteria.

Versioning: `orchestrator_global` writes DoD v1 (`og-author-dod`), then refines it after the first iteration (`og-refine-dod`) → v2, v3… without erasing history. The `architect` makes the checks concrete for the real endpoints/files/commands/containers (`ar-author-dod`), without weakening them.

## Who does what (separation)
- **tester** — RUNS `dod_eval.py` (`ts-run-dod`), collects per-check pass/fail + a weighted score. Does NOT issue a verdict.
- **evaluator** — RUNS the DSPy metric (`ev-score-dod`) and ISSUES the verdict (`ev-verdict`): keep / rollback / next-iteration / stop.

`dod_eval.py`, `dod.json`, `dspy_eval.py` are immutable for executors.

## DSPy eval (`dspy_eval.py`)
- DoD as a DSPy metric: a numeric score (0..1) + textual feedback (program-/predictor-level).
- Optionally **GEPA** — reflective prompt optimization for "pick the simplest task" and "assess readiness".
- **Reflection LM** — set in the config (NVIDIA endpoint, `NVIDIA_API_KEY`).

## DSPy everywhere (`skills/tools/dspy/`)
Beyond the DoD metric, every profile judgement call is an optimizable DSPy program, not an
ad-hoc prompt. The toolkit (`lm.py` → `signatures.py` → `programs.py` → `run.py`, optimized by
`optimize.py`) exposes one CLI; profiles call it through the shared skill `dspy-decide`:

| `--name` | Decision | Profile |
|---|---|---|
| `qualify_lead` / `pick_simplest_task` | is it a payable lead / which is simplest | orchestrator_global |
| `author_dod` / `refine_dod` | lead → program.md + checks / tighten DoD | orchestrator_global |
| `research_enough` | enough refs or next query | researcher |
| `evaluator_verdict` | keep / rollback / next / stop | evaluator |
| `build_offer` / `analyze_reply` | offer text / reply sentiment+status | sales |

Best practices applied: two LMs (cheap working + strong reflection), model-agnostic env,
save/load compiled programs (`compiled/<name>.json`), few-shot/MIPRO/GEPA optimizers, and
nightly re-optimization over harvested `data/*.jsonl`. See
[skills/tools/dspy/README.md](../skills/tools/dspy/README.md).

## Verdicts
| Verdict | When | orchestrator_sprint action |
|---|---|---|
| keep | DoD achieved | commit, → orchestrator_global |
| rollback | the last iteration worsened the metric | roll back to the previous state |
| next-iteration | partial, there is progress, limits not exhausted | new iteration |
| stop | limits exhausted / no progress | sprint failed, report |
