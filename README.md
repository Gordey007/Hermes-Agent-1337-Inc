# Hermes Agent Accelerated Business

An autonomous revenue agent that lives on a VPS (**NemoHermes + OpenShell + Hermes Agent**).
It finds leads on X/Twitter, builds a small Python/Next.js product for each one with a
multi-agent team of profiles inside an isolated docker environment, sells through **Stripe**,
and delivers the artifact from **MinIO** after payment — then learns from the run and improves
its own skills before the next day.

Built for the **Hermes Agent Accelerated Business** hackathon (NVIDIA × Stripe × NousResearch).

---

## What it does (the loop a human watches)

```
cron tweet search ──▶ leads table (sqlite)
        ▼
ORCHESTRATOR_GLOBAL (cron */30) ── qualifies leads, picks ONE tweet, versions the DoD
        ▼
ORCHESTRATOR_SPRINT ── runs one sprint, coordinates the team:
   researcher ─▶ architect ─▶ developer (+sub-agents) ─▶ tester ─▶ evaluator
   (research/)  (design/)    (product/, docker-compose)  (reports/)  (verdict)
        ▼  isolated compose, eval by DoD, iteration limits
   success ─▶ artifacts to MinIO ─▶ SALES (cron) ── offer → x.com → Stripe(TEST) → presigned link
   failure ─▶ evaluator writes reports/ to MinIO; everything except reports/ is dropped
        ▼
   evaluator records what worked/failed into memory/ and evolves the skills (see below)
```

Every step is a visible task in **Hermes-kanban**, so a person can monitor the whole run.

---

## Architecture

### Two-level orchestration

- **L0** — the host Hermes agent: bootstrap, monitoring, healthcheck, incidents.
- **L1** — `orchestrator_global` (cron): the global loop "one lead → product → sale → next day".
- **L2** — `orchestrator_sprint`: a single sprint with the team (researcher / architect /
  developer / tester / evaluator). `sales` is a separate profile on the global-loop side.

Each L2 profile is a `delegate_task` child of the sprint orchestrator. Profiles never share a
context window — they exchange work through the **shared sprint work dir** and **kanban tasks**.

### The engine — Karpathy three-file contract

A product is built by eval-gated iteration in isolation:

- `dod_eval.py` + `dod.json` + `dod.md` — the **immutable evaluator** (the agent never edits it).
- `product/` — the **agent-modifiable** implementation.
- `program.md` — the plain-English direction (tweet text + the architect's system design).

Two nested loops with hard limits: **inner ≤10** per component (CodeAct → `dod_eval` →
keep/rollback), **outer ≤10** (plan / redirect / stop). All DoD met → artifacts to MinIO.

### Everything is a skill

One piece of logic = one `SKILL.md`, with fixed sections **WHO / WHEN / STEPS / OUTPUT / NEXT /
LIMITS**. A profile does not improvise "who I am and what to do" — it reads its skill and knows
who it is, where to start, what to do, what to record and where, and to whom to hand off. The
heavy lifting (HTTP, cleaning, indexing, DSPy, evolution) lives in real Python CLIs under
`skills/tools/`; the skills just decide *when* to call them and *how to read* their compact JSON.

### Self-improvement via memory

The agent gets better day over day instead of repeating mistakes:

- As profiles work they **`record`** concrete lessons into an append-only
  `memory/lessons.jsonl` (`{ts, skill, profile, sprint, outcome: worked|failed|evolved, lesson,
  evidence}`).
- At sprint teardown the evaluator **`propose`s** an improvement from those lessons and
  **`bump`s** the skill to a new **version** — the old `SKILL.md` is archived under
  `versions/SKILL.v<old>.md`, never overwritten. Roll-back is just copying it back.
- This is driven by the `skill-evolve` skill (`skills/_shared/skill-evolve/`) over
  `skills/tools/skill_evolve/skill_evolve.py`. The same convention extends to `AGENT.md`
  personalities and sub-agent prompts. Memory survives the sprint via `reports/` → MinIO
  `hermes-reports/`, so knowledge persists across days like `reports/` itself.

---

## Repository layout

| Path | What it is |
|---|---|
| `01_x_lead/` | Tweet search → `leads` sqlite table |
| `02_sales_pipeline/` | Global orchestrator (cron) + sales: MinIO → Stripe → x.com |
| `03_auto_research/` | The engine: inner/outer loops, DoD, docker isolation, DSPy eval, scaffolding |
| `04_team/` | Multi-agent team — `profiles/` (8 profiles) + `kanban/` |
| `skills/` | Hermes `SKILL.md` procedures (one per action) + `skills/tools/` real CLIs |
| `cron/` | Cron job definitions (`crontab.yaml`) + idempotent applier |
| `infra/` | docker-compose (MinIO + sandbox) + `naming.py` (single source of names) |
| `docs/` | Multi-document design docs (start at `docs/00_overview.md`) |
| `demo/` | A worked example product + DoD evaluator |
| `memory/` | Append-only lessons the agent learns from (created at runtime) |

---

## Setup — a dialogue with the Hermes agent

There is **no `./install.sh` and no manual checklist to copy-paste**. The whole point of this
project is that the Hermes agent configures itself. Setup is a **conversation**: you talk to the
host (L0) Hermes agent and it finishes wiring everything up — fills in the config files, creates
its own working files, applies the OpenShell policies, registers the cron blueprints, and
initializes the database and MinIO buckets.

What that looks like in practice:

1. **Bring the agent online** on the VPS (NemoHermes + OpenShell + Hermes Agent) and give it
   this repository. The runbook for the box itself is in
   [`docs/12_vps_setup.md`](docs/12_vps_setup.md).
2. **Start the dialogue.** Ask the L0 agent to bootstrap the system. Driven by the `l0-bootstrap`
   skill, it will:
   - read `env.example`, ask you for the tokens it is missing, and write its own runtime config
     (it creates the files it needs — you do not hand-author them);
   - create the 8 profiles (`hermes profile create <name> --clone`), install each profile's
     skills, and apply the OpenShell network policies;
   - initialize the `leads` sqlite DB and the MinIO buckets (`hermes-artifacts`,
     `hermes-reports`);
   - register the cron blueprints (tweet search, `orchestrator_global` */30, `sales`).
3. **Keep talking to monitor and correct.** From then on you interact through the conversation
   and through Hermes-kanban — ask for status, healthchecks, or to intervene on a stuck sprint
   (`l0-monitor`, `l0-healthcheck`, `l0-incident`).
4. **It improves itself as it runs.** You do not need to hand-tune the skills, the `AGENT.md`
   personalities, or the sub-agent prompts. The team records what worked and what failed into
   `memory/` and rewrites its own skills into better, **versioned** ones (see *Self-improvement
   via memory* above) — so the files, skills, and sub-agents you started with are not the ones
   you end up with: they get better with every sprint.

> The repository ships the **design and the procedures**; the agent supplies the **configuration
> and the working state**. You converse; it self-configures and then self-improves.

---

## Principles

- **Profile = preset** (`hermes profile create <name> --clone`): `AGENT.md` (personality),
  skills, env, OpenShell policies, `config.yaml`.
- **Everything through skills** — one piece of logic = one `SKILL.md`
  (WHO/WHEN/STEPS/OUTPUT/NEXT/LIMITS).
- **Everything through Hermes-kanban** — every sprint step is visible to a human.
- **Strict naming** via `infra/naming.py` — tasks, containers, directories, MinIO keys.
- **`reports/` survives the sprint** — knowledge accumulates across days; everything else is dropped.
- **Self-improvement via memory** — profiles `record` outcomes and `skill-evolve` rewrites their
  skills into better, versioned ones; old versions are archived, never overwritten.

---

## Security

Never commit real credentials. The autonomous Stripe pipeline uses the **TEST** key (`sk_test_`)
only; the live key `rk_live_` is **forbidden** on the VPS, and keys are never logged. Fill secrets
into a local `.env` (copied from `env.example`) that is git-ignored — see
[`SECURITY.md`](SECURITY.md) for the full policy.

## License

[MIT](LICENSE).
