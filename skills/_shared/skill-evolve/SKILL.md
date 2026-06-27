---
name: skill-evolve
description: Improve a SKILL.md during real work — record what worked/failed into memory, then write a NEW versioned skill (archiving the old) from those accumulated lessons. The mechanism by which profiles, skills and sub-agents get better day over day.
version: 1.0.0
author: hermes-team
license: MIT
metadata:
  hermes:
    requires_toolsets: [python]
---

# skill-evolve

## WHO
Any profile that just finished using one of its own skills and learned something — most
often the **evaluator** at sprint teardown (it already writes `reports/final.md`), but also
researcher/architect/developer/sales after a clear win or failure with a skill.

## WHEN
- A skill produced a noticeably good or bad outcome and you can name *why* → `record` it now,
  while the lesson is concrete. One line per lesson; never wait and reconstruct later.
- The sprint is closing (evaluator `ev-final-report`/`ev-push-reports`) → `propose` for each
  skill that earned ≥1 lesson this sprint, and `bump` the ones with a clear improvement.
- Memory is the cross-day knowledge: it lives in `$HERMES_MEMORY_DIR/lessons.jsonl` and is the
  same accumulated experience that survives a sprint via `reports/` → MinIO `hermes-reports/`.

## STEPS
1. **Record a lesson** (during work, as soon as it's clear):
   ```bash
   uv run skills/tools/skill_evolve/skill_evolve.py record \
     --skill rs-github-search --profile researcher --outcome worked \
     --lesson "search-code beats search-repos for finding the exact integration file" \
     --sprint hab_2068739_s1 --evidence "research/03_*.md"
   ```
   `--outcome` is `worked` or `failed`. Keep `--lesson` to one specific, actionable sentence.
2. **Propose** an improvement from the accumulated memory for a skill (read-only):
   ```bash
   uv run skills/tools/skill_evolve/skill_evolve.py propose \
     --skill-path skills/researcher/rs-github-search
   ```
   Read the JSON: `worked[]` (turn into explicit STEPS), `failed[]` (turn into LIMITS guards),
   current `version`, and `hint`. If `lessons_total` is 0, stop — nothing earned yet.
3. **Author the new body**: rewrite the SKILL.md body keeping the WHO/WHEN/STEPS/OUTPUT/NEXT/
   LIMITS sections; fold the `worked` lessons into STEPS and the `failed` ones into LIMITS.
   Save it to a temp file (e.g. `/tmp/new_body.md`).
4. **Bump** — write the new version, archiving the old one automatically:
   ```bash
   uv run skills/tools/skill_evolve/skill_evolve.py bump \
     --skill-path skills/researcher/rs-github-search \
     --body-file /tmp/new_body.md --profile researcher --sprint hab_2068739_s1 \
     --changelog "prefer search-code; cap fetch-clean at 8 to stay under rate limit"
   ```
   It copies the old file to `versions/SKILL.v<old>.md`, sets `version` to the next minor,
   prepends a `## Changelog` line, and records the evolution back into memory.

## OUTPUT
- `memory/lessons.jsonl` — append-only lessons (`worked`/`failed`/`evolved`), the knowledge base.
- `skills/<…>/<skill>/SKILL.md` — the improved skill, version bumped, with a `## Changelog` entry.
- `skills/<…>/<skill>/versions/SKILL.v<old>.md` — the archived prior version (roll-back point).
- All commands print compact JSON to stdout — read that, never the raw skill body into context.

## NEXT
- evaluator: after `bump`, mention improved skills in `reports/final.md` so the next day starts
  from the better version; then `ev-push-reports`.
- Any profile: next time you load the skill you get the improved body automatically — no wiring.
- To roll back a regression: copy the relevant `versions/SKILL.v<old>.md` back over `SKILL.md`.

## LIMITS
- Do NOT `bump` without lessons — improvements must come from recorded evidence, not guesses.
- One concrete change per `bump`; keep the `--changelog` specific so history stays auditable.
- Never put secrets, tokens or full file contents in a lesson — only short, generalizable notes.
- Minor-version bumps only (x.Y.z → x.(Y+1).0); a breaking redesign is a human/architect call.
- Memory path is `$HERMES_MEMORY_DIR` (default `./memory`); keep it inside the repo/work dir so
  it is committed/pushed with `reports/`, not lost on teardown.
