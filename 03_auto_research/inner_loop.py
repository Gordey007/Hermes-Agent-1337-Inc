"""Inner loop (≤10/component): CodeAct in docker-compose → dod_eval → keep/rollback.

This is a loop harness, not a code generator: the actual code-editing step is done by the
Hermes agent (developer/sub-agent role). `agent_step` is a callback the agent implements via
its skill; the harness invokes it, runs the immutable dod_eval, keeps the edit when the metric
goes up (keep) or reverts it (rollback), and logs to state.

Snapshot/rollback is implemented as a file copy of the product/ directory (snapshot before the step).
"""
from __future__ import annotations

import shutil
from pathlib import Path
from typing import Callable

from dod_eval import evaluate
from state import SprintState

MAX_INNER = 10

# agent_step(product_dir, component, feedback) -> str  (text: what it did)
AgentStep = Callable[[str, str, str], str]


def _snapshot(product: Path, snap: Path) -> None:
    if snap.exists():
        shutil.rmtree(snap)
    shutil.copytree(product, snap)


def _restore(product: Path, snap: Path) -> None:
    if not snap.exists():
        return
    shutil.rmtree(product)
    shutil.copytree(snap, product)


def run_inner(sprint_dir: str, component: str, dod_path: str,
              agent_step: AgentStep, max_inner: int = MAX_INNER) -> dict:
    state = SprintState(sprint_dir)
    product = Path(sprint_dir) / "product"
    snap = Path(sprint_dir) / f".snap_{component}"
    feedback = ""

    for i in range(1, max_inner + 1):
        _snapshot(product, snap)
        action = agent_step(str(product), component, feedback)
        result = evaluate(str(product), dod_path)
        score, feedback = result["score"], result["feedback"]

        kept = state.keep_if_better(score)
        if not kept:
            _restore(product, snap)  # roll back the failed edit
        state.log("inner", i, action, score, kept, feedback, component)

        if score >= 1.0:
            shutil.rmtree(snap, ignore_errors=True)
            return {"component": component, "iterations": i, "score": score, "done": True}

    shutil.rmtree(snap, ignore_errors=True)
    return {"component": component, "iterations": max_inner,
            "score": state.best_score, "done": False, "feedback": feedback}


if __name__ == "__main__":
    # demo stub for agent_step (the real step is the Hermes agent)
    def _demo(product_dir, component, feedback):
        return f"noop on {component} (feedback was: {feedback[:60]})"
    import sys
    print(run_inner(sys.argv[1], sys.argv[2], sys.argv[3], _demo))
