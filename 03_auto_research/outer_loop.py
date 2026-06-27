"""Outer loop (≤10): the planner decomposes the product into components, runs inner for
each, and once all DoDs pass, uploads the artifacts to MinIO and updates the lead status.

This is Karpathy's top-level loop harness. The concrete decisions "which component is next /
redirect / stop" are made by the planner agent (`planner` callback) — Hermes
orchestrator_sprint implements it via its skills (os-decide-next).

three-file contract: program.md (the direction) immutable from architect, dod.json immutable,
product/ — agent-modifiable. After completion — drop-all-except-reports + docker down -v.
"""
from __future__ import annotations

import shutil
import subprocess
from pathlib import Path
from typing import Callable

from dod_eval import evaluate
from inner_loop import run_inner
from state import SprintState

MAX_OUTER = 10

# planner(sprint_dir, last_score, feedback, done_components) -> dict
#   returns {"action": "build"|"redirect"|"stop", "component": "...", "dod": "path"}
Planner = Callable[[str, float, str, list], dict]
# agent_step is passed through to inner_loop
AgentStep = Callable[[str, str, str], str]


def _teardown(sprint_dir: str, docker_project: str | None) -> None:
    """drop-all-except-reports: tear down containers and working directories, keep reports/."""
    if docker_project:
        subprocess.run(["docker", "compose", "-p", docker_project, "down", "-v"],
                       capture_output=True, text=True)
    sd = Path(sprint_dir)
    for sub in ("research", "design", "product"):
        shutil.rmtree(sd / sub, ignore_errors=True)
    for snap in sd.glob(".snap_*"):
        shutil.rmtree(snap, ignore_errors=True)


def run_outer(sprint_dir: str, planner: Planner, agent_step: AgentStep,
              docker_project: str | None = None, max_outer: int = MAX_OUTER) -> dict:
    state = SprintState(sprint_dir)
    done_components: list[str] = []
    last_score, feedback = 0.0, ""

    for o in range(1, max_outer + 1):
        plan = planner(sprint_dir, last_score, feedback, done_components)
        action = plan.get("action", "stop")
        state.log("outer", o, f"planner→{action} {plan.get('component','')}", last_score,
                  kept=True, feedback=plan.get("note", ""))

        if action == "stop":
            break

        component = plan["component"]
        dod = plan["dod"]
        res = run_inner(sprint_dir, component, dod, agent_step)
        last_score, feedback = res["score"], res.get("feedback", "")
        if res["done"] and component not in done_components:
            done_components.append(component)

        # all of the sprint's DoDs fully passed?
        whole = evaluate(str(Path(sprint_dir) / "product"), plan.get("sprint_dod", dod))
        if whole["score"] >= 1.0:
            state.log("outer", o, "ALL DoD met", whole["score"], kept=True,
                      feedback=whole["feedback"])
            return {"done": True, "outer_iterations": o, "score": whole["score"],
                    "components": done_components, "sprint_dir": sprint_dir}

    return {"done": False, "outer_iterations": max_outer, "score": last_score,
            "components": done_components, "feedback": feedback, "sprint_dir": sprint_dir}


if __name__ == "__main__":
    import sys
    # demo: one component, stubs (the real planner/agent_step are Hermes agents)
    def _planner(sd, score, fb, done):
        if "app" in done:
            return {"action": "stop"}
        return {"action": "build", "component": "app", "dod": sys.argv[2],
                "sprint_dod": sys.argv[2]}
    def _step(product, comp, fb):
        return f"noop {comp}"
    print(run_outer(sys.argv[1], _planner, _step))
