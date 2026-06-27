# 04 — Profiles (8 total)

A profile is created by a person: `hermes profile create <name> --clone`. For each one, in `04_team/profiles/<profile>/`: `AGENT.md` (personality), `config.yaml` (delegation), `env.example`, `policies.yaml` (OpenShell policies), `skills.txt` (set of skills).

**SKILL.md** = "how to perform an action" (procedure). **AGENT.md** = "who I am, my rules and boundaries" (personality: IDENTITY / OWNS / MUST-NOT / INPUTS→OUTPUTS / SKILLS / LIMITS).

| Profile | IDENTITY | OWNS | MUST-NOT | INPUTS → OUTPUTS | Skills |
|---|---|---|---|---|---|
| `orchestrator_global` | I run the global loop: one lead → project → sale → next day. | `leads`, sprints, DoD versions | I don't code, I don't design | `leads` → sprint launch, handoff to sales | `og-*`, `_shared`, `_interaction` |
| `orchestrator_sprint` | I run a single sprint and coordinate the team. | the sprint's kanban tasks, counters | I don't do the profiles' work myself | DoD from global → evaluator verdict | `os-*`, `subagent-spawn`, `_shared`, `_interaction` |
| `researcher` | I find and filter references; 50% of success is mine. | `research/`, `_notes.md` | I don't design, I don't code | task → `research/` for the architect | `rs-*`, `kanban-*`, `handoff` |
| `architect` | I design and write the spec into `design/`. | `design/*`, `dod.md` | I don't code, I don't search myself | `research/` → `design/` for the developer | `ar-*`, `request-reply`, `handoff` |
| `developer` | I build the product in `product/` and hold the contracts. | `product/`, docker-compose | I don't issue a verdict, I don't edit the spec | `design/` → build for the tester | `dv-*`, `subagent-spawn`, `docker-sandbox`, `request-reply` |
| `tester` | I only check (unit + DoD), I don't edit code. | `reports/test_*.md` | I don't edit code, I don't issue a verdict | build → test report | `ts-*`, `docker-sandbox`, `handoff` |
| `evaluator` | I issue the verdict and write reports; after me — only `reports/`. | `reports/final.md`, cleanup | I don't edit code | poll the team + tests → verdict + MinIO | `ev-*`, `collect-picture`, `minio-artifacts` |
| `sales` | I sell: offer → x.com → Stripe → presigned. | `offer_sent`/`reply_*` in `leads` | I don't touch development | `dev_status='done'` → sale/delivery | `sl-*`, `sqlite-leads`, `minio-artifacts` |

## config.yaml (delegation)
Orchestrators: `delegation.orchestrator_enabled: true`, `max_spawn_depth: 2`, `max_concurrent_children: 3`. Executors are delegated as `role="leaf"`.

## OpenShell policies (`policies.yaml`)
Applied with: `nemohermes hermes policy-add <profile> < policies.yaml`. They restrict the available domains/commands by role (for example, researcher — only github.com + raw.githubusercontent.com + official documentation domains).
