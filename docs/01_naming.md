# 01 — Naming Convention

All names are generated through `infra/naming.py` (the single source of truth). Prefix `hab` (Hermes Accelerated Business) + short `<tweetid>` (last 7 digits) + `s<sprint>` + role/component. The goal: a person monitoring reads names unambiguously, and scripts don't create drift.

| Entity | Template | Example | Function |
|---|---|---|---|
| Kanban task | `hab-<tweetid>-s<sprint>-<role>-<seq>` | `hab-2068739-s1-arch-01` | `task_id()` |
| Docker project (`-p`) | `hab_<tweetid>_s<sprint>` | `hab_2068739_s1` | `docker_project()` |
| Docker container | `hab_<tweetid>_s<sprint>_<component>` | `hab_2068739_s1_backend` | `container_name()` |
| Compose config | `infra/compose/hab_<tweetid>_s<sprint>.yml` | — | `compose_path()` |
| Sprint directory | `/sandbox/work/hab_<tweetid>/s<sprint>/` | — | `sprint_dir()` |
| └ research | `.../research/` | `research/01_*.md` | `research_dir()` |
| └ design | `.../design/` | `design/system-design.md` | `design_dir()` |
| └ product | `.../product/` | — | `product_dir()` |
| └ reports (NOT dropped) | `.../reports/` | `reports/final.md` | `reports_dir()` |
| MinIO artifact | `hermes-artifacts/hab_<tweetid>/v<outer>/<file>` | — | `artifact_key()` |
| MinIO report | `hermes-reports/hab_<tweetid>/s<sprint>.md` | — | `report_key()` |
| Profile session | `hab_<tweetid>_<profile>` | `hab_2068739_researcher` | `session_name()` |

## Role codes (in kanban tasks)
`oglob` (orchestrator_global), `osprint` (orchestrator_sprint), `res` (researcher), `arch` (architect), `dev` (developer), `test` (tester), `eval` (evaluator), `sales`.

## How to read a name
`hab-2068739-s1-arch-01` → project for tweet …2068739, sprint 1, architect's task, sequence 01.
`hab_2068739_s1_backend` → the backend container in the sandbox of sprint 1 for this tweet.

## Rule
Any skill that creates a task/container/directory/key MUST call the corresponding `naming.py` function rather than build the string by hand.
