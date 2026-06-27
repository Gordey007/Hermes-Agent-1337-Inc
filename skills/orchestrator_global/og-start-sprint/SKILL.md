---
name: og-start-sprint
description: Create the sprint, the root kanban task, names via naming.py, and launch orchestrator_sprint.
version: 1.0.0
author: hermes-team
license: MIT
metadata:
  hermes:
    requires_toolsets: [python, sqlite]
    requires_tools: [delegate_task, kanban_create]
---

# og-start-sprint

## WHO
orchestrator_global.

## WHEN
- DoD v1 is ready for the lead in work.

## STEPS
1. `naming`: `docker_project`/`work_dir` for `hab_<tweetid>_s<sprint>` (sprint=1 on the first run).
2. Create the working directory `/sandbox/work/hab_<tweetid>/s<sprint>/` with subdirectories research/design/product/reports.
3. Place `dod.json`/`dod.md` (v1) into `design/`.
4. Create the root kanban task: `kanban_create(title="hab-<tweetid>-s<sprint>-orch-01", assignee="orchestrator_sprint", tenant="hab_<tweetid>")` — this is the parent for all of the sprint's phase tasks.
5. `subagent-spawn` → `delegate_task` orchestrator_sprint (goal=build the product to meet the DoD; context=paths,
   tweet_id, sprint, limits 5/5/10/10).

## OUTPUT
- A running orchestrator_sprint + the root task + a ready sprint working directory.

## NEXT
- Wait for the sprint verdict. `done` → `og-handoff-sales`. `failed` (after the 1st iteration) → `og-refine-dod` or `og-close-day`.

## LIMITS
- One active sprint. Do not interfere with orchestrator_sprint's work (it coordinates the team itself).
