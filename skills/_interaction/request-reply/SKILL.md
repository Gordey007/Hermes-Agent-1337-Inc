---
name: request-reply
description: A "request→reply" protocol between profiles with an iteration limit (≤5).
version: 1.0.0
author: hermes-team
license: MIT
metadata:
  hermes:
    requires_tools: [kanban_create, kanban_link, kanban_comment]
    requires_toolsets: [python]
---

# request-reply

## WHO
architect→researcher (needs more references), developer→architect (needs spec clarification).

## WHEN
- You lack the information needed to continue your phase.

## STEPS
1. Check the counter: `python 04_team/kanban/counters.py get --tweet <tweetid> --sprint <N> --counter <architect_researcher|dev_architect>`. `over_limit` → do NOT request, `escalate`.
2. Formulate a SPECIFIC request (what exactly is needed, for which component/DoD criterion).
3. Increment: `python 04_team/kanban/counters.py inc --tweet <tweetid> --sprint <N> --counter <counter>`.
4. Create a request task for the addressee: `kanban_create(title="hab-<tweetid>-s<N>-<addressee>-req", assignee="<addressee_profile>", tenant="hab_<tweetid>", body="<question>")` + `kanban_link(parent=<my_task_id>, child=<req_task_id>)`.
5. Wait for the reply (the addressee writes the result to the shared directory + `kanban_complete`), read its summary/metadata via `kanban_show`.

## OUTPUT
- An incremented iteration counter + a reply artifact in the shared directory.

## NEXT
- Got the reply → continue my phase. Still missing info and counter < 5 → repeat; otherwise `escalate`.

## LIMITS
- ≤5 iterations per pair (architect_researcher / dev_architect). Exceeding → `escalate` to orchestrator_sprint.
