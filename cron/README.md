# `cron/` — how the autonomous pipeline is wired over time

This directory is the answer to "when does each component run and how do they hand off?".
Everything in the system is connected by **five Hermes cron jobs** ([crontab.yaml](crontab.yaml));
nothing else schedules itself. Apply them with `uv run cron/apply.py`.

A Hermes cron job is three things: a **NAME**, a **TASK** (the natural-language prompt the
agent executes), and a **CRON expression**. Orchestration jobs drive the kanban board through
the built-in `kanban-orchestrator` skill (`hermes kanban create --assignee <profile> ...`).

## The timeline

```
X_LEAD_HUNTER            CREATE_PROJECT_AND_OFFER        SALES_FOLLOWUP
(hourly)                 (daily 01:00)                   (every 6h)
   │                          │                              │
   ▼                          ▼                              ▼
leads table  ───pick one──►  sprint (03 + 04)  ──done──►  offer → Stripe → deliver
(dev_status                  orchestrator_sprint          sl-* skills, presigned MinIO
 =pending)                   researcher→architect→
                             developer→tester→evaluator
                                  │
                             SPRINT_WATCHDOG (every 30m) recovers stuck sprints
                             HEALTHCHECK    (every 15m) keeps the OS alive
```

## Job-by-job

| Job | Schedule | Owner profile | Wires |
|---|---|---|---|
| `X_LEAD_HUNTER` | `0 * * * *` | orchestrator_global | X API → `leads` table (ingest only) |
| `CREATE_PROJECT_AND_OFFER` | `0 1 * * *` | orchestrator_global | `leads` → sprint → MinIO → hand off to sales |
| `SPRINT_WATCHDOG` | `*/30 * * * *` | orchestrator_sprint | recovers/kills stuck sprints; never starts new ones |
| `SALES_FOLLOWUP` | `0 */6 * * *` | sales | `dev_status='done'` → offer → Stripe → presigned delivery |
| `HEALTHCHECK` | `*/15 * * * *` | orchestrator_global | DB / docker / MinIO / tokens watchdog |

## How a project actually gets built (the global → sprint handoff)

`CREATE_PROJECT_AND_OFFER` does **not** build the product itself. It:

1. Picks one lead and authors the initial DoD.
2. **Generates the sprint program from templates** —
   `uv run 03_auto_research/scaffold.py --tweet <id> --sprint 1 --direction "<tweet>" --dod-from-tweet`.
   This emits a self-contained `run_sprint.py` (the iteration harness), `program.md`,
   `dod.json`, and the `product/` skeleton into the sprint directory
   (`/sandbox/work/hab_<tweetid>/s1/`). See [../03_auto_research/README.md](../03_auto_research/README.md).
3. Creates the root kanban task (`kanban-orchestrator`) and launches the generated
   `run_sprint.py`, which drives the inner/outer loops with `orchestrator_sprint` and the
   profile team (researcher → architect → developer → tester → evaluator).
4. On all-DoD-met, uploads artifacts to MinIO and sets `dev_status='done'` — which is the
   single signal `SALES_FOLLOWUP` waits on.

The contract between jobs is the **`leads` table state machine**:
`pending → in_progress → done|failed`, then `offer_sent → reply_status`.
No job reaches into another's internals; they only read/advance lead state and the kanban board.
