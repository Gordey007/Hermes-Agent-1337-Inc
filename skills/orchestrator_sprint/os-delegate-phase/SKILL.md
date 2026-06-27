---
name: os-delegate-phase
description: Delegate the phase to the right profile via subagent-spawn (package goal+context).
version: 1.0.0
author: hermes-team
license: MIT
metadata:
  hermes:
    requires_toolsets: [python]
    requires_tools: [delegate_task, kanban_show]
---

# os-delegate-phase

## WHO
orchestrator_sprint.

## WHEN
- The phase task is in `todo`, the previous phase is `done` (or this is the first phase).

## STEPS
1. Determine the phase profile: research→researcher, design→architect, dev→developer, test→tester, eval→evaluator.
2. `subagent-spawn` → `delegate_task(role="leaf", profile=<profile>)`. Into `context`, package: the working
   directory paths, tweet_id, sprint, `dod.json`, limits, the phase's expected OUTPUT.
3. The phase task already has `assignee=<profile>` — `hermes gateway` spawns the worker automatically (the status moves to `Running` on its own). Track the run: `kanban_show(<task_id>)` / `hermes kanban runs <task_id>`.

## OUTPUT
- A running phase profile + the task in `in_progress`.

## NEXT
- `os-track-iterations` (watch the limits) → once the phase is ready, `os-collect-status`.

## LIMITS
- max_concurrent_children:3, max_spawn_depth:2. One phase at a time (except parallel components within dev).
