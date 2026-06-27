"""Unified name generator (end-to-end naming for monitoring).

All pipeline entities are named through these functions so that a human monitoring the
system reads names unambiguously, and scripts don't drift out of sync. The prefix is `hab`
(Hermes Accelerated Business).

Templates:
  kanban task        hab-<tweetid>-s<sprint>-<role>-<seq>     hab-2068739-s1-arch-01
  docker project     hab_<tweetid>_s<sprint>                  hab_2068739_s1
  docker container   hab_<tweetid>_s<sprint>_<component>      hab_2068739_s1_backend
  compose config     infra/compose/hab_<tweetid>_s<sprint>.yml
  sprint directory   /sandbox/work/hab_<tweetid>/s<sprint>/
  MinIO artifact     hermes-artifacts/hab_<tweetid>/v<outer>/<file>
  MinIO report       hermes-reports/hab_<tweetid>/s<sprint>.md
  profile session    hab_<tweetid>_<profile>                  hab_2068739_researcher
"""
from __future__ import annotations

import re

PREFIX = "hab"
WORK_ROOT = "/sandbox/work"
ARTIFACTS_BUCKET = "hermes-artifacts"
REPORTS_BUCKET = "hermes-reports"

# Short role codes for kanban tasks.
ROLE_CODES = {
    "orchestrator_global": "oglob",
    "orchestrator_sprint": "osprint",
    "researcher": "res",
    "architect": "arch",
    "developer": "dev",
    "tester": "test",
    "evaluator": "eval",
    "sales": "sales",
}


def _short_tweet_id(tweet_id: str | int) -> str:
    """Short tail of tweet_id (last 7 digits) — compact and unique for monitoring."""
    digits = re.sub(r"\D", "", str(tweet_id))
    return digits[-7:] if len(digits) > 7 else digits


def _slug(text: str, max_len: int = 40) -> str:
    s = re.sub(r"[^a-z0-9]+", "-", str(text).lower()).strip("-")
    return s[:max_len].strip("-")


def role_code(role: str) -> str:
    return ROLE_CODES.get(role, _slug(role, 8))


def task_id(tweet_id: str | int, sprint: int, role: str, seq: int) -> str:
    return f"{PREFIX}-{_short_tweet_id(tweet_id)}-s{sprint}-{role_code(role)}-{seq:02d}"


def docker_project(tweet_id: str | int, sprint: int) -> str:
    return f"{PREFIX}_{_short_tweet_id(tweet_id)}_s{sprint}"


def container_name(tweet_id: str | int, sprint: int, component: str) -> str:
    return f"{docker_project(tweet_id, sprint)}_{_slug(component, 20)}"


def compose_path(tweet_id: str | int, sprint: int) -> str:
    return f"infra/compose/{docker_project(tweet_id, sprint)}.yml"


def sprint_dir(tweet_id: str | int, sprint: int) -> str:
    return f"{WORK_ROOT}/{PREFIX}_{_short_tweet_id(tweet_id)}/s{sprint}"


def research_dir(tweet_id: str | int, sprint: int) -> str:
    return f"{sprint_dir(tweet_id, sprint)}/research"


def design_dir(tweet_id: str | int, sprint: int) -> str:
    return f"{sprint_dir(tweet_id, sprint)}/design"


def product_dir(tweet_id: str | int, sprint: int) -> str:
    return f"{sprint_dir(tweet_id, sprint)}/product"


def reports_dir(tweet_id: str | int, sprint: int) -> str:
    """The only directory that survives drop-all-except-reports."""
    return f"{sprint_dir(tweet_id, sprint)}/reports"


def artifact_key(tweet_id: str | int, outer: int, filename: str) -> str:
    return f"{ARTIFACTS_BUCKET}/{PREFIX}_{_short_tweet_id(tweet_id)}/v{outer}/{filename}"


def report_key(tweet_id: str | int, sprint: int) -> str:
    return f"{REPORTS_BUCKET}/{PREFIX}_{_short_tweet_id(tweet_id)}/s{sprint}.md"


def session_name(tweet_id: str | int, profile: str) -> str:
    return f"{PREFIX}_{_short_tweet_id(tweet_id)}_{profile}"


def research_artifact(seq: int, slug: str) -> str:
    """Name of a research artifact file inside research/ (without directory): NN_slug.md."""
    return f"{seq:02d}_{_slug(slug)}.md"


if __name__ == "__main__":
    tid = "1234567892068739"
    print("task_id        ", task_id(tid, 1, "architect", 1))
    print("docker_project ", docker_project(tid, 1))
    print("container      ", container_name(tid, 1, "backend"))
    print("sprint_dir     ", sprint_dir(tid, 1))
    print("artifact_key   ", artifact_key(tid, 2, "app.zip"))
    print("report_key     ", report_key(tid, 1))
    print("research_file  ", research_artifact(3, "FastAPI Stripe Example"))
