---
name: kanban-read
description: Read your own and parent kanban tasks and iteration counters via the built-in Hermes kanban.
version: 1.0.0
author: hermes-team
license: MIT
metadata:
  hermes:
    requires_tools: [kanban_show, kanban_list]
---

# kanban-read

## WHO
Any team profile (L1/L2 and executors).

## WHEN
- At the start of your phase — to understand what's expected of you (the parent task) and how high the iteration counter has already climbed.

## STEPS
Kanban is a built-in Hermes tool (shared DB `~/.hermes/kanban.db`). Act via tool calls, do NOT write your own SQL.

1. Find sprint tasks: `kanban_list(tenant="hab_<tweetid>")` (filter by your `assignee`/status). A human sees the same via `hermes kanban list --tenant hab_<tweetid>`.
2. Your task: `kanban_show(<task_id>)` → read the title (`hab-<tweetid>-s<sprint>-<role>-<seq>`), `status`, the comment thread, `metadata` (the input handoff artifact from the previous profile).
3. The parent task (from orchestrator_sprint) — to understand the phase goal and the link to the DoD.
4. Iteration counters: `python 04_team/kanban/counters.py get --tweet <tweetid> --sprint <N> --counter <name>` (a sidecar; the native kanban does not store them).

## OUTPUT
- The profile's context gains: the current status, the input artifact (path in the shared directory / MinIO key), counter values (`dev_architect`/`architect_researcher`/`github_search`/`inner_loop`/`outer_loop`).

## NEXT
- Read → I perform the profile-specific skill actions; when done — `kanban-write`.

## LIMITS
- Read only. Status/counter changes go through `kanban-write`.
