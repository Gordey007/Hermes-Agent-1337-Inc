"""DSPy wrapper around the immutable DoD: DoD as a metric (numeric score + textual
feedback), plus optional GEPA for optimizing the "pick the simplest task" and
"readiness assessment" prompts.

The DoD metric is the single source of truth. DSPy here does not "re-evaluate"; it
wraps the result of `dod_eval.evaluate` into a `dspy.Prediction`-compatible metric format
(score + feedback) suitable for program-/predictor-level optimization and GEPA reflection.

The reflection LM is taken from config (env DSPY_REFLECTION_MODEL / DSPY_LM_BASE / NVIDIA_API_KEY),
so that reflection is driven by a strong model while the main work is done by the working one.

The dspy dependency is optional: without it the pure `dod_metric` metric is still available.
"""
from __future__ import annotations

import os

from dod_eval import evaluate

import dspy  # type: ignore
_HAS_DSPY = True


def dod_metric(product_dir: str, dod_path: str, *, with_feedback: bool = True):
    """Metric for DSPy/GEPA: returns score [0..1] and (optionally) textual feedback.

    Compatible with GEPA (feedback-aware): when with_feedback=True it returns an object with
    .score and .feedback, otherwise just a float.
    """
    res = evaluate(product_dir, dod_path)
    score, feedback = res["score"], res["feedback"]
    if not with_feedback:
        return score
    if _HAS_DSPY and hasattr(dspy, "Prediction"):
        return dspy.Prediction(score=score, feedback=feedback)
    return {"score": score, "feedback": feedback}


def _configure_reflection_lm():
    """Bring up the reflection LM from config (NVIDIA-compatible OpenAI endpoint)."""
    if not _HAS_DSPY:
        raise RuntimeError("dspy is not installed — GEPA unavailable")
    model = os.getenv("DSPY_REFLECTION_MODEL", "openai/nvidia/llama-3.1-nemotron-70b-instruct")
    base = os.getenv("DSPY_LM_BASE", "https://integrate.api.nvidia.com/v1")
    api_key = os.getenv("NVIDIA_API_KEY") or os.getenv("OPENAI_API_KEY")
    return dspy.LM(model, api_base=base, api_key=api_key, temperature=1.0)


def optimize_with_gepa(program, trainset, *, dod_path_key: str = "dod_path"):
    """Optional GEPA optimization of the program's prompts against the DoD metric.

    program — dspy.Module ("pick the simplest task" / "readiness assessment").
    trainset — examples with product_dir/dod_path fields.
    """
    if not _HAS_DSPY:
        raise RuntimeError("dspy is not installed")
    reflection_lm = _configure_reflection_lm()

    def metric(example, pred, trace=None, pred_name=None, pred_trace=None):
        return dod_metric(getattr(pred, "product_dir", example.product_dir),
                          getattr(example, dod_path_key), with_feedback=True)

    gepa = dspy.GEPA(metric=metric, reflection_lm=reflection_lm,
                     max_full_evals=int(os.getenv("GEPA_MAX_EVALS", "5")))
    return gepa.compile(program, trainset=trainset, valset=trainset)


if __name__ == "__main__":
    import argparse
    import json
    ap = argparse.ArgumentParser(description="DoD as a DSPy metric")
    ap.add_argument("--product", required=True)
    ap.add_argument("--dod", required=True)
    args = ap.parse_args()
    out = dod_metric(args.product, args.dod)
    payload = out if isinstance(out, dict) else {"score": getattr(out, "score", out),
                                                 "feedback": getattr(out, "feedback", "")}
    print(json.dumps(payload, ensure_ascii=False, indent=2))
