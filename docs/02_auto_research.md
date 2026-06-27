# 02 — Auto-Development Engine (inner/outer loops)

The `03_auto_research/` subproject. Eval-gated iterative development in isolation, following Karpathy's principle (three-file contract).

## Three-file contract
- **`dod_eval.py`** — the **immutable** evaluator (DoD checks). The agent NEVER changes it. Separated from the product code.
- **agent-modifiable implementation** — the product code in `product/`.
- **`program.md`** — the plain-English direction (Karpathy `program.md`): tweet text + system-design from the architect. Authored by the architect/evaluator, executed by the developer.

Plus `dod.json` (machine-readable checks) and `dod.md` (human-readable criteria) — also not edited by executors (only versioned by the orchestrator).

## Inner loop (≤10 per component) — `inner_loop.py`
1. CodeAct edits the component in the docker-compose sandbox.
2. Run `dod_eval` → metric.
3. **keep** when the metric improves, otherwise **rollback** to the previous state.
4. Persistence: `progress.jsonl` (one line per step) + `session.md` (context).
5. Only `research/`+`design/`+`product/`+`reports/` are kept; then `docker compose -p <proj> down -v`.

## Outer loop (≤10) — `outer_loop.py`
1. The planner decomposes/redirects/stops.
2. All DoD met → artifacts to MinIO + status in `leads`.

## Template-based sprint generation — `scaffold.py` + `templates/`
The engine is immutable; each sprint's *program* is **generated**, not hand-written. `og-start-sprint`
calls `scaffold.py`, which renders `templates/` (via `string.Template.safe_substitute`) into the
sprint directory using names from `infra/naming.py`:

```
scaffold.py --tweet <id> --sprint <N> --direction "<lead text>" [--root /sandbox]
  → <sprint_dir>/
       program.md       ← templates/program.md.tmpl        (IMMUTABLE direction)
       dod.json         ← templates/dod.json.tmpl          (IMMUTABLE DoD, 4 default checks)
       product/README.md← templates/product_readme.md.tmpl (product skeleton)
       run_sprint.py    ← templates/run_sprint.py.tmpl     (the iteration harness, ALWAYS regenerated)
```

`run_sprint.py` binds the immutable engine (`outer_loop.run_outer` + `inner_loop` + `dod_eval`) to
THIS sprint's paths/DoD/docker project, and dispatches each phase to a profile as a kanban task
(built-in `kanban-orchestrator` skill). Contract files are written once (idempotent, never
clobbered); the derived `run_sprint.py` is regenerated every run. This is what gives "the agent
creates a program file with iterations" — by template, not by hand.

## Iteration limits (counters in kanban)
- developer↔architect ≤5
- architect↔researcher ≤5
- github-search ≤10
- inner-loop ≤10 (per component)
- outer-loop ≤10

Exceeding the limit → the evaluator writes a report, the sprint is `failed`.

## Files
`dod_eval.py`, `inner_loop.py`, `outer_loop.py`, `state.py`, `dspy_eval.py`, `scaffold.py`,
`docker-compose.tmpl.yml`, `templates/` (`program.md.tmpl`, `dod.json.tmpl`,
`product_readme.md.tmpl`, `run_sprint.py.tmpl`), `README.md`.

See [cron/README.md](../cron/README.md) for *when* sprints start (the global loop wires
`scaffold.py` → kanban → `run_sprint.py` on a schedule).
