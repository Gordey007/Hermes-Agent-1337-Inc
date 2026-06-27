---
name: os-plan-sprint
description: Break the sprint into phases (research→design→dev→test→eval) and create tasks.
version: 1.0.0
author: hermes-team
license: MIT
metadata:
  hermes:
    requires_tools: [kanban_create, kanban_link]
    requires_toolsets: [python]
---

# os-plan-sprint

## WHO
orchestrator_sprint (L2).

## WHEN
- orchestrator_global has delegated the sprint (there is `dod.json` v1 + working directory `s<sprint>/`).

## STEPS
1. Read `design/dod.json` and the task text (`context` from global).
2. Create phase child tasks in the built-in kanban (`kanban_create` + `kanban_link` to the root, `assignee=<phase profile>`, `tenant=hab_<tweetid>`) following the title naming `hab-<tweetid>-s<sprint>-<role>-<seq>`:
   research → design → dev → test → eval (dependencies in order via `kanban_link`).
3. Reset the sidecar iteration counters: `python 04_team/kanban/counters.py reset --tweet <tweetid> --sprint <N>`.

## OUTPUT
- A set of phase tasks in kanban + zeroed-out counters.

## NEXT
- `os-delegate-phase` for the first phase (research → researcher).

## LIMITS
- I do not do the profiles' work myself. Phases are strictly sequential (one active at a time).
