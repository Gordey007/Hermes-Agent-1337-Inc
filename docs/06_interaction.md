# 06 — Profile Interaction

Exchanging artifacts happens through the **shared sprint working directory** (`/sandbox/work/hab_<tweetid>/s<sprint>/`). Status/progress — through **kanban tasks**. Coordination — the small-loop orchestrator.

## Interaction skills (`skills/_interaction/`)
| Skill | Action |
|---|---|
| `handoff` | Handoff between profiles: what to pack into the kanban artifact, how to mark it "ready to receive", and to whom. |
| `request-reply` | "request→reply" with an iteration limit: how to phrase it, where to record it, how to count iterations. |
| `collect-picture` | Poll several profiles: what's done/not done/planned/failed/remaining. Used by the evaluator and orchestrator_sprint. |
| `escalate` | On a limit overrun/blocker: escalate to the orchestrator + record the reason. |

## Sprint pipeline
```
researcher ──handoff──▶ architect ──handoff──▶ developer ──handoff──▶ tester ──handoff──▶ evaluator
     ▲                       │                      │
     └──request-reply(≤5)────┘                      │
     (architect→researcher)   ◀──request-reply(≤5)──┘
                                (developer→architect)
```

## Iteration limits (counters in kanban)
| Link | Limit | Counter |
|---|---|---|
| developer ↔ architect | ≤5 | `dev_architect` |
| architect ↔ researcher | ≤5 | `architect_researcher` |
| github-search | ≤10 | `github_search` |
| inner-loop (component) | ≤10 | `inner_loop` |
| outer-loop | ≤10 | `outer_loop` |

Exceeding → `escalate` → the evaluator writes a report → the sprint is `failed`.

## Shared-directory rule
researcher → architect → developer write into the shared directory; the evaluator places reports into `reports/`; everything except `reports/` is dropped (`ev-cleanup`).
