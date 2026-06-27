---
name: og-author-dod
description: Draft the initial DoD from the tweet text — what counts as "product is ready".
version: 1.0.0
author: hermes-team
license: MIT
metadata:
  hermes:
    requires_toolsets: [python]
---

# og-author-dod

## WHO
orchestrator_global.

## WHEN
- The lead has been taken into work (`dev_status='in_progress'`), the sprint has not started yet.

## STEPS
1. Read the lead's `tweet_text` (`sqlite-leads`).
2. Formulate verifiable acceptance criteria → `dod.json` (format 03): an array of `checks`
   with `id`/`kind` (`http`/`file_exists`/`contains`/`cmd`)/`weight`.
3. Write the initial DoD as version `v1` into the sprint working directory (`design/dod.md` + machine-readable `dod.json`).

## OUTPUT
- `dod.json` (machine-readable, immutable input for `dod_eval`) + human-readable `dod.md`, version v1.

## NEXT
- `og-start-sprint` (create the sprint and launch orchestrator_sprint with this DoD).

## LIMITS
- The DoD must be GENUINELY verifiable automatically (every check is machine-readable). Refinement comes later in `og-refine-dod`.
