# 00 — Architecture Overview

**Hermes Agent Accelerated Business** — an autonomous agent on a VPS (NemoHermes + OpenShell + Hermes Agent) that earns money on its own: it finds leads on X/Twitter, builds a Python/Next.js product for them with a multi-agent team of profiles in an isolated docker environment, sells through Stripe, and delivers the artifact from MinIO after payment.

## Flow (what a person sees while monitoring)

```
cron tweet search ──▶ leads table (sqlite)
        │
        ▼
ORCHESTRATOR_GLOBAL (cron */30) ── qualifies leads, picks ONE tweet
        │  creates sprint + root kanban task, versions the DoD
        ▼
ORCHESTRATOR_SPRINT ── runs a single sprint, coordinates the team:
   researcher ──▶ architect ──▶ developer (+sub-agents by role) ──▶ tester ──▶ evaluator
   (research/)   (design/)      (product/, docker-compose)        (reports/test) (verdict)
        │  all inside an isolated compose, eval by DoD, iteration limits
        ▼
   success ──▶ artifacts to MinIO (hermes-artifacts), dev_status='done'
        │         │
        │         ▼
        │   SALES (cron 0 * * * *) ── offer → x.com → Stripe(TEST) → low-pressure dialog
        │                              ── payment → presigned MinIO link (short TTL)
        ▼
   failure ──▶ evaluator writes reports/ to MinIO (hermes-reports), everything except reports/ is dropped
```

## Two-level orchestration

- **L0** — the main Hermes agent (host): bootstrap, monitoring, healthcheck, incidents.
- **L1** — `orchestrator_global` (cron): the global loop "one lead → product → sale → next day".
- **L2** — `orchestrator_sprint`: a single sprint, the team of profiles (researcher/architect/developer/tester/evaluator).
- `sales` — a separate profile on the global-loop side.

## Principles

- **Profile = preset** (`hermes profile create <name> --clone`). For each one: `AGENT.md` (personality), a set of skills, `env`, OpenShell policies, `config.yaml` (delegation).
- **Sub-agents — dynamically** via the `subagent-spawn` skill on top of `delegate_task` (clean context → the skill packs everything into `goal`+`context`).
- **Everything through skills** — one piece of logic = one `SKILL.md` (WHO/WHEN/STEPS/OUTPUT/NEXT/LIMITS).
- **Everything through Hermes-kanban** (a built-in tool: `kanban_*` tool-calls + worker lanes by `assignee`) — every sprint step is visible to a person.
- **Strict naming** (`infra/naming.py`) — tasks, containers, directories, MinIO keys.
- **`reports/` survives the sprint** — knowledge accumulates across days; everything else is dropped.
- **Self-improvement via memory** — profiles `record` what worked/failed into `memory/lessons.jsonl` and use the `skill-evolve` skill to rewrite their own skills into better, **versioned** ones; old versions are archived, never overwritten (see `docs/08_skills.md`).

## Document map
- `01_naming.md` — naming convention.
- `02_auto_research.md` — inner/outer loops, three-file contract.
- `03_eval.md` — DoD + DSPy/GEPA.
- `04_profiles.md` — 8 profiles.
- `05_subagents.md` — sub-agents and roles.
- `06_interaction.md` — interaction, limits.
- `07_kanban.md` — built-in Hermes-kanban (tool-calls, lanes, gateway).
- `12_vps_setup.md` — step-by-step VPS launch.
- `08_skills.md` — skills registry + AGENT.md.
- `09_github_research.md` — GitHub smart-search.
- `10_sales.md` — sales funnel.
- `11_infra.md` — docker-compose, MinIO, networks.
