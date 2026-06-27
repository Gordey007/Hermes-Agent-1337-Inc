"""Typed DSPy signatures — the declarative I/O contracts for every LLM decision in the
pipeline. One signature per decision point; the prose in each docstring/field is the
*initial* instruction that the optimizers (optimize.py) later improve automatically.

DSPy best practice followed here:
  * inputs/outputs are typed (bool / Literal / list) so the adapter parses them reliably;
  * field descriptions are short and task-specific (they become the optimization target);
  * no orchestration logic lives here — just the contract.

If dspy is missing the module still imports (signatures degrade to plain objects) so that
tooling that only needs the names does not crash.
"""
from __future__ import annotations

from typing import Literal

import dspy  # type: ignore
_Signature = dspy.Signature
InputField = dspy.InputField
OutputField = dspy.OutputField
_HAS_DSPY = True



# --- orchestrator_global ----------------------------------------------------------------
class QualifyLead(_Signature):
    """Decide whether an X/Twitter post is a real lead: someone who wants a small
    software product built and could plausibly pay for it (not a bot, not a rant)."""

    tweet_text: str = InputField(desc="raw text of the post")
    is_relevant: bool = OutputField(desc="true only if it is a buildable, payable need")
    intent: Literal["willing_to_pay", "hiring", "looking_for_tool", "none"] = OutputField(
        desc="the buyer intent category"
    )
    reason: str = OutputField(desc="one short sentence justifying the decision")


class PickSimplestTask(_Signature):
    """From several qualified leads pick the ONE that is simplest to build end-to-end in a
    single sprint (smallest scope, clearest done-criteria, least external dependencies)."""

    candidates: str = InputField(desc="JSON list of {tweet_id, text} qualified leads")
    chosen_tweet_id: str = OutputField(desc="tweet_id of the simplest lead")
    justification: str = OutputField(desc="why it is the simplest to deliver")


class AuthorDoD(_Signature):
    """Turn a lead (and any design notes) into a machine-checkable Definition of Done:
    concrete file/command/http checks that prove the product satisfies the request."""

    tweet_text: str = InputField(desc="the lead text = the goal")
    design_notes: str = InputField(desc="architect notes, may be empty")
    direction: str = OutputField(desc="plain-English program.md body: what to build")
    dod_checks: str = OutputField(
        desc="JSON list of checks [{id,kind,...,weight}] for dod.json; kinds: file_exists/contains/cmd/http"
    )


class RefineDoD(_Signature):
    """After a sprint, tighten or relax the DoD based on what the evaluator reported as
    unreachable, missing, or under-specified. Keep it honest and still buyer-meaningful."""

    prev_dod: str = InputField(desc="previous dod.json content")
    evaluator_report: str = InputField(desc="evaluator's reports/final.md summary")
    refined_dod: str = OutputField(desc="updated JSON list of checks")
    changelog: str = OutputField(desc="one line per change and why")


# --- researcher -------------------------------------------------------------------------
class ResearchEnough(_Signature):
    """Decide if the gathered references are enough to start designing, or what to search
    next. Stops context bloat: judge from the notes summary, not raw content."""

    notes: str = InputField(desc="research/_notes.md useful/skip map + summaries")
    found_count: int = InputField(desc="how many artifacts gathered so far")
    enough: bool = OutputField(desc="true if the architect can proceed")
    next_query: str = OutputField(desc="if not enough, the next search query; else empty")


# --- evaluator --------------------------------------------------------------------------
class EvaluatorVerdict(_Signature):
    """Given the DoD feedback, the test report and the current iteration, decide the sprint
    action. 'keep'=accept current best, 'rollback'=restore prev, 'next'=iterate again,
    'stop'=give up and write the report."""

    dod_feedback: str = InputField(desc="textual feedback from dod_eval (failed checks)")
    test_report: str = InputField(desc="tester reports/test_*.md summary")
    iteration: int = InputField(desc="current inner-loop attempt (1..10)")
    verdict: Literal["keep", "rollback", "next", "stop"] = OutputField(desc="the action")
    rationale: str = OutputField(desc="one short sentence")


# --- sales ------------------------------------------------------------------------------
class BuildOffer(_Signature):
    """Write a short, non-pushy, personal offer for the lead, referencing what was actually
    built. No hype, no spam — one clear value sentence plus a soft call to action."""

    tweet_text: str = InputField(desc="the original lead text")
    product_summary: str = InputField(desc="what the team delivered")
    offer_text: str = OutputField(desc="<=280 chars, friendly, specific, no hard sell")


class AnalyzeReply(_Signature):
    """Classify the lead's reply so the pipeline can update leads.reply_status and decide
    the next (cooldown-respecting) touch."""

    reply_text: str = InputField(desc="the lead's reply")
    sentiment: Literal["positive", "negative", "neutral"] = OutputField()
    reply_status: Literal["interested", "paid", "declined", "no_signal"] = OutputField()
    summary: str = OutputField(desc="one short sentence the sales profile stores")


# Registry: program name -> (Signature, recommended module type).
# 'cot' = ChainOfThought (reasoning), 'predict' = Predict (cheap classification).
SIGNATURES = {
    "qualify_lead": (QualifyLead, "predict"),
    "pick_simplest_task": (PickSimplestTask, "cot"),
    "author_dod": (AuthorDoD, "cot"),
    "refine_dod": (RefineDoD, "cot"),
    "research_enough": (ResearchEnough, "predict"),
    "evaluator_verdict": (EvaluatorVerdict, "cot"),
    "build_offer": (BuildOffer, "cot"),
    "analyze_reply": (AnalyzeReply, "predict"),
}
