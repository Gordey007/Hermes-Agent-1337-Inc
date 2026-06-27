# 05 — Sub-agents and Component Development

## subagent-spawn (on top of delegate_task)
Sub-agents are created **dynamically**, not as preconfigured profiles. The `subagent-spawn` skill calls `delegate_task(goal, context, role="leaf", profile=...)`.

**Key feature:** the sub-agent gets a **CLEAN context** — it does not see the parent's history. Therefore the skill MUST pack everything needed into `goal` + `context`: the full component specification, container names from the contract, the relevant DoD checks, the boundaries (what NOT to touch).

Delegation limits: `max_spawn_depth: 2`, `max_concurrent_children: 3`.

## Component development (developer)
Via `dv-spawn-subagent`, the `developer` brings up one sub-agent per component and holds **end-to-end contract consistency**: table field ↔ backend ↔ API ↔ frontend UI (`dv-component-contract`).

Roles (skills `dv-role-*`):
- `dv-role-ml-python` — ML component in Python.
- `dv-role-backend-python` — backend in Python.
- `dv-role-django-python` — Django service.
- `dv-role-frontend-nextjs` — Next.js/TypeScript frontend.

Each sub-agent = its own component in its own container `hab_<tweetid>_s<sprint>_<component>` with a health endpoint for the DoD. Names are taken from `design/api-contract.md` + `design/component-*.md` unchanged. TypeScript — only for the frontend, everything else Python. None of the sub-agents edit `dod_eval.py`.

## Inner loop in a sub-agent
Each component iterates ≤10 times (`inner_loop`): edit → `dod_eval` → keep/rollback. When information is missing, the sub-agent signals the developer → who then runs `dv-request-architect` (≤5).
