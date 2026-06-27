# 08 — Skills Registry

**Principle:** a skill = a deterministic prompt instruction. One skill = one action. A profile does NOT figure out "who I am and what to do" — it reads its skill and understands: who it is → where to start → what to do → what to record/where → what comes next → to whom to hand off. This brings the work of AI profiles closer to deterministic.

## SKILL.md structure
Frontmatter: `name` / `description` / `version` / `author` / `license` + `metadata.hermes` (`requires_toolsets` / `requires_tools` / optional `blueprint.schedule`). Body — fixed sections:
- **WHO** — the role in this action.
- **WHEN** — trigger/precondition (kanban status, input artifact).
- **STEPS** — numbered steps (which tool/skill to call).
- **OUTPUT** — what to record and where (per `naming.py`).
- **NEXT** — to whom to hand off / which status / next skill.
- **LIMITS** — iteration limits and what to do when exceeded.

Catalog: `skills/<profile>/<skill>/SKILL.md` + shared ones in `skills/_shared/`, `skills/_interaction/`, `skills/l0/`.

## Shared (`skills/_shared/`)
`sqlite-leads`, `kanban-read`, `kanban-write`, `naming`, `minio-artifacts`, `docker-sandbox`, `dspy-decide`, `skill-evolve`.

## Self-improving skills (memory-driven)
Skills are not frozen. As profiles work they accumulate **memory** — an append-only log of what
worked and what failed — and use it to rewrite their own skills into better, **versioned** ones.
This is how files, skills and sub-agents get better day over day instead of repeating mistakes.

- **Memory store:** `$HERMES_MEMORY_DIR/lessons.jsonl` (default `./memory/`), one JSON lesson per
  line: `{ts, skill, profile, sprint, outcome: worked|failed|evolved, lesson, evidence}`. It is the
  same accumulated experience that survives a sprint via `reports/` → MinIO `hermes-reports/` (and
  so persists across days, like `reports/` itself — see `docs/02_auto_research.md`).
- **The `skill-evolve` skill** (`skills/_shared/skill-evolve/`) drives the real CLI
  `skills/tools/skill_evolve/skill_evolve.py` with three actions:
  - `record` — append a concrete lesson while the outcome is fresh (any profile, during work).
  - `propose` — read the lessons for a skill + its current version → an improvement brief
    (`worked[]` → STEPS, `failed[]` → LIMITS). Read-only.
  - `bump` — write a NEW `SKILL.md` (minor version bump), archiving the old one under
    `<skill>/versions/SKILL.v<old>.md` and prepending a `## Changelog` entry. Roll-back = copy the
    archived version back. The evolution itself is recorded to memory (`outcome: evolved`).
- **Who & when:** mostly the **evaluator** at sprint teardown (it already authors `reports/final.md`
  and pushes reports), but any profile may `record` a lesson the moment a skill clearly helped or
  hurt. Improvements come only from recorded evidence — never `bump` on a guess.
- The same convention applies to AGENT.md personalities and sub-agent prompts: improvements are
  proposed from memory, versioned, and archived — nothing is overwritten blindly.

## Interaction (`skills/_interaction/`)
`handoff`, `request-reply`, `collect-picture`, `escalate`, `subagent-spawn`.

## L0 (`skills/l0/`)
`l0-bootstrap`, `l0-monitor`, `l0-healthcheck`, `l0-incident`.

## orchestrator_global (`skills/orchestrator_global/`)
`og-qualify-lead`, `og-pick-task`, `og-author-dod`, `og-refine-dod`, `og-start-sprint`, `og-handoff-sales`, `og-close-day`, `og-global-report`.

## orchestrator_sprint (`skills/orchestrator_sprint/`)
`os-plan-sprint`, `os-delegate-phase`, `os-track-iterations`, `os-collect-status`, `os-decide-next`, `os-teardown`.

## researcher (`skills/researcher/`)
`rs-plan-research`, `rs-github-search`, `rs-web-docs`, `rs-clean-context`, `rs-write-notes`, `rs-decide-enough`, `rs-handoff-architect`.

## architect (`skills/architect/`)
`ar-read-research`, `ar-system-design`, `ar-data-model`, `ar-api-contract`, `ar-component-spec`, `ar-author-dod`, `ar-request-research`, `ar-handoff-developer`.

## developer (`skills/developer/`)
`dv-read-spec`, `dv-scaffold`, `dv-spawn-subagent`, `dv-role-ml-python`, `dv-role-backend-python`, `dv-role-django-python`, `dv-role-frontend-nextjs`, `dv-component-contract`, `dv-integrate`, `dv-request-architect`, `dv-handoff-tester`.

## tester (`skills/tester/`)
`ts-read-dod`, `ts-author-unit-tests`, `ts-run-tests`, `ts-run-dod`, `ts-test-report`, `ts-handoff-evaluator`.

## evaluator (`skills/evaluator/`)
`ev-collect-picture`, `ev-score-dod`, `ev-verdict`, `ev-final-report`, `ev-cleanup`, `ev-push-reports`.

## sales (`skills/sales/`)
`sl-build-offer`, `sl-send-x`, `sl-stripe-invoice`, `sl-dialog`, `sl-analyze-reply`, `sl-deliver`.

## AGENT.md (personality)
Separate from skills. Sections: IDENTITY / OWNS / MUST-NOT / INPUTS→OUTPUTS / SKILLS / LIMITS. See `docs/04_profiles.md`.
