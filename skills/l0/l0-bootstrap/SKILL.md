---
name: l0-bootstrap
description: Bring up the system — check env/tokens, create profiles, install skills, apply policies, initialize DBs.
version: 1.0.0
author: hermes-team
license: MIT
metadata:
  hermes:
    requires_toolsets: [shell, python, sqlite]
---

# l0-bootstrap

## WHO
The main Hermes agent (L0, host) — once, at system startup.

## WHEN
- First start or after reinstalling the VPS/OpenShell.

## STEPS
1. Check env/tokens (filled from `env.example`): `GITHUB_TOKEN`, `STRIPE_API_KEY_TEST` (sk_test_), `NVIDIA_API_KEY`,
   `X_BEARER_TOKEN`, `X_USER_ACCESS_TOKEN`. Do NOT load the live key `rk_live_`.
2. Create 8 profiles: `hermes profile create <name> --clone` for orchestrator_global, orchestrator_sprint,
   researcher, architect, developer, tester, evaluator, sales.
3. For each profile: copy `04_team/profiles/<name>/{AGENT.md,config.yaml,policies.yaml}`,
   fill in env from `env.example`, install skills from `skills.txt` into `~/.hermes/skills/`.
4. Apply OpenShell policies: `nemohermes hermes policy-add <profile> < policies.yaml`.
5. Initialize the built-in Hermes kanban: `hermes kanban init` (DB `~/.hermes/kanban.db`); leads DB: `python 01_x_lead/create_db.py`.
6. Bring up the infra: `docker compose -f infra/docker-compose.yml up -d` (MinIO + networks, buckets hermes-artifacts/hermes-reports).
7. Start the kanban-lane dispatcher: `hermes gateway start` (spawns workers by `assignee`).
8. Set up cron for orchestrator_global (`*/30 * * * *`) and sales (`0 * * * *`).

## OUTPUT
- Ready profiles, the leads DB (`leads`) + the built-in kanban, an active gateway, MinIO with buckets, policies, cron.

## NEXT
- `l0-healthcheck` to verify. After that the system is autonomous: cron → orchestrator_global.

## LIMITS
- Run once. Do not log tokens. Before re-running — `l0-healthcheck`.
