"""DSPy LM configuration — single place that wires DSPy to the NVIDIA endpoint.

Two language models, per DSPy best practice:
  * the WORKING LM  — does the task (cheap/fast, NemoHermes by default);
  * the REFLECTION LM — drives optimizer reflection (GEPA/MIPRO), a stronger model.

Both read the same NVIDIA-compatible OpenAI endpoint from env so the whole pipeline is
model-agnostic: swap the model names without touching any program.

Env:
  NVIDIA_API_KEY            — required to actually call the model
  DSPY_LM_BASE              — default https://integrate.api.nvidia.com/v1
  DSPY_WORKING_MODEL        — default openai/nvidia/nemotron-4-340b-instruct
  DSPY_REFLECTION_MODEL     — default openai/nvidia/llama-3.1-nemotron-70b-instruct

The dspy import is optional: helpers raise a clear error if dspy is missing, so the
rest of the repo keeps importing this module without a hard dependency.
"""
from __future__ import annotations

import os

import dspy  # type: ignore
_HAS_DSPY = True

_BASE = "https://integrate.api.nvidia.com/v1"
_WORKING = "openai/nvidia/nemotron-4-340b-instruct"
_REFLECTION = "openai/nvidia/llama-3.1-nemotron-70b-instruct"


def _require_dspy() -> None:
    if not _HAS_DSPY:
        raise RuntimeError("dspy is not installed — run `uv sync --extra dspy`")


def _api_key() -> str | None:
    return os.getenv("NVIDIA_API_KEY") or os.getenv("OPENAI_API_KEY")


def working_lm():
    """The task LM (cheap, fast). Used to run programs."""
    _require_dspy()
    return dspy.LM(
        os.getenv("DSPY_WORKING_MODEL", _WORKING),
        api_base=os.getenv("DSPY_LM_BASE", _BASE),
        api_key=_api_key(),
        temperature=float(os.getenv("DSPY_TEMPERATURE", "0.2")),
        cache=True,
    )


def reflection_lm():
    """The strong LM that proposes better instructions during optimization."""
    _require_dspy()
    return dspy.LM(
        os.getenv("DSPY_REFLECTION_MODEL", _REFLECTION),
        api_base=os.getenv("DSPY_LM_BASE", _BASE),
        api_key=_api_key(),
        temperature=1.0,
    )


def configure(working=None):
    """Set the global DSPy LM. Call once before running/optimizing programs."""
    _require_dspy()
    dspy.configure(lm=working or working_lm())
