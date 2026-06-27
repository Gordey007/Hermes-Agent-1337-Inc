"""DSPy program registry — turns each signature into a runnable Module and loads a
compiled (optimized) artifact from compiled/<name>.json when one exists.

Design:
  * one program per decision point (see signatures.SIGNATURES);
  * Predict for cheap classification, ChainOfThought for anything needing reasoning;
  * if compiled/<name>.json exists, its few-shot demos + tuned instructions are loaded
    (this is how optimize.py output is picked up — zero code change for callers).

Callers (run.py / skills) only need `load(name)` → a callable program.
"""
from __future__ import annotations

import os
from pathlib import Path

from signatures import SIGNATURES

import dspy  # type: ignore
_HAS_DSPY = True

HERE = Path(__file__).resolve().parent
COMPILED = Path(os.getenv("DSPY_COMPILED_DIR", str(HERE / "compiled")))


def _require_dspy() -> None:
    if not _HAS_DSPY:
        raise RuntimeError("dspy is not installed — run `uv sync --extra dspy`")


def build(name: str):
    """Construct a fresh zero-shot program for `name` from its signature."""
    _require_dspy()
    if name not in SIGNATURES:
        raise KeyError(f"unknown program '{name}' (known: {', '.join(SIGNATURES)})")
    sig, kind = SIGNATURES[name]
    if kind == "cot":
        return dspy.ChainOfThought(sig)
    return dspy.Predict(sig)


def compiled_path(name: str) -> Path:
    return COMPILED / f"{name}.json"


def load(name: str):
    """Return the program for `name`, loading compiled demos/instructions if present."""
    prog = build(name)
    path = compiled_path(name)
    if path.exists():
        prog.load(str(path))
    return prog


def list_programs() -> list[str]:
    return sorted(SIGNATURES)
