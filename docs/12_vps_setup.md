# 12. Launch on a VPS — step-by-step runbook

The order of actions for deploying the autonomous system on a VPS with NemoHermes + OpenShell.
Each step — what to do and how to verify it. Follow strictly in order: each next step
relies on the previous one. There are no destructive operations except those explicitly marked.

> Security: the real keys are in `хакатон.md`. They MUST NOT be logged, posted outward, or
> sent to external services. The autonomous Stripe pipeline uses ONLY the test key
> `STRIPE_API_KEY_TEST` (`sk_test_...`). Do NOT load the live key `rk_live_...` onto the VPS.

---

## Step 0 — prerequisites (one-time)

1. The VPS is up, SSH access exists, Docker + docker compose are installed: `docker version && docker compose version`.
2. NemoHermes + OpenShell are installed, the CLIs are available:
   - `hermes --version`
   - `nemohermes --help`
3. Python 3.11+ and `uv`: `python --version && uv --version`.
4. The repository is cloned into the working directory, dependencies: `uv sync` (from the project root).

Check: `hermes --version`, `docker compose version`, `uv --version` — all without errors.

---

## Step 1 — environment and tokens

1. Copy `env.example` → the working env of the profiles and fill it from `хакатон.md`:
   - `GITHUB_TOKEN` (`ghp_...`)
   - `STRIPE_API_KEY_TEST` (`sk_test_...`) — **test only**
   - `NVIDIA_API_KEY` (`nvapi-...`)
   - `X_BEARER_TOKEN`, `X_USER_ACCESS_TOKEN`
   - `LEADS_DB_PATH=/sandbox/x_lead/leads.db`, `COUNTERS_DB_PATH=/sandbox/kanban/counters.db`
   - MinIO: `MINIO_ENDPOINT`, `MINIO_ACCESS_KEY`, `MINIO_SECRET_KEY`
2. Do NOT enter the live key `rk_live_`.

Check: `env | grep -E 'GITHUB_TOKEN|STRIPE_API_KEY_TEST|NVIDIA_API_KEY|X_BEARER'` shows the values;
`env | grep rk_live` — empty.

---

## Step 2 — Hermes profiles (8 of them)

The operator creates the profiles themselves (presetting), one at a time:

```bash
hermes profile create orchestrator_global --clone
hermes profile create orchestrator_sprint --clone
hermes profile create researcher          --clone
hermes profile create architect           --clone
hermes profile create developer           --clone
hermes profile create tester              --clone
hermes profile create evaluator           --clone
hermes profile create sales               --clone
```

Check: `hermes profile list` shows all 8.

---

## Step 3 — profile configs, personalities, and policies

For each profile `<name>`:

1. Copy `04_team/profiles/<name>/{AGENT.md,config.yaml,policies.yaml}` into the Hermes profile directory.
2. Fill the profile's env from `env.example` (Step 1).
3. Install the profile's skills from its `skills.txt` into `~/.hermes/skills/`
   (shared ones from `skills/_shared/` and `skills/_interaction/` — to everyone who needs them).
4. Apply the OpenShell policies: `nemohermes hermes policy-add <name> < 04_team/profiles/<name>/policies.yaml`.

Key `config.yaml` settings:
- For orchestrators: `delegation.orchestrator_enabled: true`, `max_spawn_depth: 2`, `max_concurrent_children: 3`.
- For auto-routing of the parent task: `kanban.orchestrator_profile` on the orchestrators.

Check: `hermes profile show orchestrator_sprint` — the config is visible; `nemohermes hermes policy-list <name>` — policies applied.

---

## Step 4 — databases

1. Leads DB: `python 01_x_lead/create_db.py` (creates `leads` at `LEADS_DB_PATH`).
2. Built-in Hermes-kanban: `hermes kanban init` (DB `~/.hermes/kanban.db`).
3. The iteration counters sidecar is created lazily on the first `inc`; the directory must exist:
   `mkdir -p /sandbox/kanban`.

Check:
- `sqlite3 $LEADS_DB_PATH "PRAGMA table_info(leads);"` contains the `tweet_id` column.
- `hermes kanban list` responds (an empty list is fine).

---

## Step 5 — infrastructure (MinIO + networks)

```bash
docker compose -f infra/docker-compose.yml up -d
```

Brings up MinIO and the networks for isolated sprints. Create the `hermes-artifacts`, `hermes-reports` buckets
(if not created by the compose init script).

Check: `docker ps` — the MinIO container is `Up`; the MinIO console is reachable; the buckets exist.

---

## Step 6 — kanban lane dispatcher (gateway)

```bash
hermes gateway start
```

The dispatcher daemon spawns workers by `task.assignee` (= profile name). Without it the phase tasks
will stay in `Ready` with a `skipped_nonspawnable` event.

Check: `hermes gateway status` — the dispatcher is alive, lanes are registered by profile names.

---

## Step 7 — cron

1. Tweet search (if not yet configured): `*/30 * * * *` → `01_x_lead/x_lead_hunter.py`.
2. Global orchestrator: `*/30 * * * *` → launch the `orchestrator_global` profile.
3. Sales: `0 * * * *` → launch the `sales` profile.

Check: `crontab -l` shows the three jobs.

---

## Step 8 — final readiness check (l0-healthcheck)

Run the checks from `skills/l0/l0-healthcheck`:
- Leads DB: `PRAGMA table_info(leads)` contains `tweet_id`.
- `hermes kanban list` responds, `hermes gateway status` — alive.
- `docker ps -a` — no stuck `hab_*` containers.
- MinIO: the `hermes-artifacts`/`hermes-reports` buckets are reachable.
- Tokens: trial read-only calls to GitHub / Stripe (TEST) / X — without 401/403.

Once it passes, the system is autonomous: cron → `orchestrator_global` → sprint (the team of profiles via
gateway lanes) → MinIO → `sales`.

---

## Operation and monitoring

- System picture: `hermes kanban list` or the dashboard `hermes dashboard` (http://127.0.0.1:9119).
- Running a specific task: `hermes kanban runs <task_id>`.
- Leads: `sqlite3 $LEADS_DB_PATH` (see `skills/l0/l0-monitor`).
- Incidents (stuck stack, expired token): `skills/l0/l0-incident`.

## Re-run / reinstall

- Steps 2–3 (profiles/policies) are done once; on a VPS reinstall — again.
- Before a repeat `l0-bootstrap` always run `l0-healthcheck`.
- Don't log tokens at any step.
