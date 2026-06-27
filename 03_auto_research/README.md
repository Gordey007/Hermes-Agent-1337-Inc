# 03_auto_research — eval-gated build engine (Karpathy three-file contract + DSPy)

Isolated, iterative product build per sprint: the agent edits the code in `product/`, the
**immutable** `dod_eval.py` judges it, the metric goes up → keep, otherwise → rollback.
Everything runs in a docker-compose sandbox; after the sprint it's drop-all-except-reports.

## Files

| File | What it is | Who calls it |
|---|---|---|
| `dod_eval.py` | **IMMUTABLE** DoD scorer (file_exists/contains/cmd/http → score [0..1] + feedback) | tester (`ts-run-dod`), inner/outer |
| `state.py` | Sprint persistence: `reports/progress.jsonl` + `reports/session.md`, keep_if_better | inner/outer |
| `inner_loop.py` | Inner loop ≤10/component: snapshot → agent_step → dod_eval → keep/rollback → log | developer/orchestrator_sprint |
| `outer_loop.py` | Outer loop ≤10: planner decomposes → inner per component → all DoD met → MinIO; teardown | orchestrator_sprint |
| `dspy_eval.py` | DoD as a DSPy metric (score+feedback) + optional GEPA for prompts | evaluator (`ev-score-dod`) |
| `docker-compose.tmpl.yml` | Template for the isolated sprint stack (naming via `infra/naming.py`) | developer (`dv-scaffold`) |

## Three-file contract

1. **`<sprint>/dod.json`** (immutable) — acceptance criteria, written by the architect
   (`ar-author-dod`), inheriting the first-pass DoD from orchestrator_global. Format:
   ```json
   { "checks": [
     {"id": "be_up", "kind": "http", "url": "http://localhost:8000/health", "expect_status": 200, "weight": 2},
     {"id": "has_readme", "kind": "file_exists", "path": "README.md"},
     {"id": "tests", "kind": "cmd", "run": "pytest -q", "expect_code": 0}
   ]}
   ```
2. **`<sprint>/program.md`** (immutable) — the direction (Karpathy `program.md`): tweet text + the architect's system design.
3. **`<sprint>/product/`** (agent-modifiable) — the product code.

`agent_step(product_dir, component, feedback)` and `planner(...)` are **callbacks**
implemented by the Hermes agent through its skills (developer/orchestrator_sprint). The
Python harness only orchestrates the loop, the snapshots, and the journal.

## Environment

```bash
export LEADS_DB_PATH=/sandbox/x_lead/leads.db        # to update lead status (outer)
export KANBAN_DB_PATH=/sandbox/kanban/tasks.db
# DSPy/GEPA (optional, evaluator only):
export NVIDIA_API_KEY=nvapi-...                       # provide via your own secret store
export DSPY_REFLECTION_MODEL=openai/nvidia/llama-3.1-nemotron-70b-instruct
export DSPY_LM_BASE=https://integrate.api.nvidia.com/v1
```

`dspy` and `httpx` are optional: without `dspy` the plain `dod_metric` is still available;
without `httpx` the DoD http checks fail (but file/cmd checks still work).

## Running it (how the team uses it)

```bash
# 1. Run DoD directly (tester / smoke)
python dod_eval.py --product /sandbox/work/hab_8739012/s1/product --dod .../s1/dod.json

# 2. Inner loop for one component (developer drives agent_step via a subagent)
#    harness: run_inner(sprint_dir, component, dod_path, agent_step)

# 3. Outer loop for the whole sprint (orchestrator_sprint drives the planner)
#    run_outer(sprint_dir, planner, agent_step, docker_project="hab_8739012_s1")

# 4. DSPy metric (evaluator, ev-score-dod)
python dspy_eval.py --product .../product --dod .../dod.json
```

## Limits (counters in kanban)

- inner ≤10 per component; outer ≤10 per sprint. On overflow `outer_loop` returns
  `done=False`, the evaluator writes `reports/final.md`, and the sprint is `failed`.

## Isolation and teardown

- The stack is brought up from `docker-compose.tmpl.yml` with `-p hab_<tweetid>_s<sprint>`
  (naming via `infra/naming.py`), on an isolated network.
- `outer_loop._teardown` = **drop-all-except-reports**: `docker compose -p <proj> down -v`,
  removal of `research/ design/ product/ .snap_*`, leaving only `reports/` (→ MinIO
  `hermes-reports/` via `ev-push-reports`).

## Persistence

`state.SprintState` writes `reports/progress.jsonl` (machine-readable) and
`reports/session.md` (human-readable): each iteration = step + score + best + KEEP/ROLLBACK.
This survives teardown and accumulates knowledge across days.

## Handoff

Outer `done=True` → orchestrator_global uploads `product/` to MinIO
`hermes-artifacts/hab_<tweetid>/v<outer>/`, sets `dev_status='done'` + `dev_artifact` in
`leads`, and hands the lead to sales (02_sales_pipeline). See
[docs/02_auto_research.md](../docs/02_auto_research.md), [docs/03_eval.md](../docs/03_eval.md).
