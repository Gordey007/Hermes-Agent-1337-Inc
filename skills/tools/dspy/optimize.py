"""Optimize a DSPy program against a labelled trainset and save the compiled artifact.

Supports the three optimizers we actually use, picked by dataset size / need:
  * bootstrap  — BootstrapFewShot: cheapest, auto-selects few-shot demos from traces.
  * mipro      — MIPROv2: jointly tunes instructions + few-shot demos (medium data).
  * gepa       — GEPA: reflective, feedback-aware (uses the reflection LM); best when the
                 metric returns textual feedback (our dod_metric / classification metrics).

The trainset is a JSONL file of {inputs:{...}, label:{...}} rows. The metric compares the
program's prediction to the label; for free-text outputs it falls back to an LM judge via
the reflection LM is avoided here — we keep metrics deterministic where possible.

Output: compiled/<name>.json (few-shot demos + tuned instructions), loaded automatically
by programs.load(). Re-run nightly (see cron note in README) to keep improving.

Usage:
    uv run skills/tools/dspy/optimize.py --name qualify_lead \
        --trainset data/qualify_lead.jsonl --optimizer bootstrap
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

import lm as lm_mod
import programs as programs_mod

import dspy  # type: ignore
from dspy.teleprompt import BootstrapFewShot, MIPROv2  # type: ignore
_HAS_DSPY = True


def _load_trainset(path: Path) -> list:
    rows = []
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line:
            continue
        row = json.loads(line)
        ex = dspy.Example(**row["inputs"], **row.get("label", {}))
        ex = ex.with_inputs(*row["inputs"].keys())
        rows.append(ex)
    return rows


def _exact_metric(example, pred, trace=None):
    """Deterministic metric: every labelled output field must match the prediction.
    Comparison is case-insensitive string equality (good for our typed/Literal outputs)."""
    for key, want in example.__dict__["_store"].items():
        if key in example.inputs().__dict__["_store"]:
            continue
        got = getattr(pred, key, None)
        if str(got).strip().lower() != str(want).strip().lower():
            return False
    return True


def optimize(name: str, trainset_path: str, optimizer: str = "bootstrap") -> str:
    if not _HAS_DSPY:
        raise RuntimeError("dspy is not installed — run `uv sync --extra dspy`")
    lm_mod.configure()
    program = programs_mod.build(name)
    trainset = _load_trainset(Path(trainset_path))

    if optimizer == "bootstrap":
        tele = BootstrapFewShot(metric=_exact_metric, max_bootstrapped_demos=4, max_labeled_demos=4)
        compiled = tele.compile(program, trainset=trainset)
    elif optimizer == "mipro":
        tele = MIPROv2(metric=_exact_metric, auto="light", prompt_model=lm_mod.reflection_lm())
        compiled = tele.compile(program, trainset=trainset, requires_permission_to_run=False)
    elif optimizer == "gepa":
        from dspy import GEPA  # type: ignore

        tele = GEPA(metric=_exact_metric, reflection_lm=lm_mod.reflection_lm(), auto="light")
        compiled = tele.compile(program, trainset=trainset)
    else:
        raise ValueError(f"unknown optimizer '{optimizer}' (bootstrap|mipro|gepa)")

    out = programs_mod.compiled_path(name)
    out.parent.mkdir(parents=True, exist_ok=True)
    compiled.save(str(out))
    return str(out)


if __name__ == "__main__":
    ap = argparse.ArgumentParser(description="Optimize a DSPy program → compiled/<name>.json")
    ap.add_argument("--name", required=True, help="program name (see signatures.SIGNATURES)")
    ap.add_argument("--trainset", required=True, help="JSONL of {inputs,label} rows")
    ap.add_argument("--optimizer", default="bootstrap", choices=["bootstrap", "mipro", "gepa"])
    args = ap.parse_args()
    saved = optimize(args.name, args.trainset, args.optimizer)
    print(json.dumps({"name": args.name, "compiled": saved, "optimizer": args.optimizer},
                     ensure_ascii=False))
