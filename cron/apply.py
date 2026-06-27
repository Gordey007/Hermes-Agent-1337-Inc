"""Apply cron/crontab.yaml to the Hermes cron daemon (idempotent).

Reads the job registry and creates/updates each Hermes cron job via the CLI:
    hermes cron create --name <NAME> --schedule "<expr>" --task "<task text>"

This is the single command that wires the whole timeline together — running it on the
VPS materializes every job in cron/crontab.yaml. Re-running it is safe: existing jobs are
updated in place (delete + create) so the registry file stays the source of truth.

Usage:
    uv run cron/apply.py            # apply all jobs
    uv run cron/apply.py --dry-run  # print the commands only
"""
from __future__ import annotations

import argparse
import shlex
import subprocess
import sys
from pathlib import Path

import yaml

REGISTRY = Path(__file__).with_name("crontab.yaml")


def _existing_jobs() -> set[str]:
    """Names already known to the cron daemon (best-effort; empty on any error)."""
    try:
        out = subprocess.run(["hermes", "cron", "list"], capture_output=True, text=True)
        return {line.split()[0] for line in out.stdout.splitlines() if line.strip()}
    except FileNotFoundError:
        return set()


def apply(dry_run: bool = False) -> int:
    jobs = yaml.safe_load(REGISTRY.read_text(encoding="utf-8")).get("jobs", [])
    existing = _existing_jobs()
    for job in jobs:
        name = job["name"]
        task = " ".join(job["task"].split())  # collapse the folded-YAML prompt to one line
        cmds = []
        if name in existing:
            cmds.append(["hermes", "cron", "delete", "--name", name])
        cmds.append(["hermes", "cron", "create", "--name", name,
                     "--schedule", job["schedule"], "--task", task])
        for cmd in cmds:
            printable = " ".join(shlex.quote(c) for c in cmd)
            if dry_run:
                print(printable)
                continue
            print(f"[cron] {printable}")
            r = subprocess.run(cmd)
            if r.returncode != 0:
                print(f"[cron] FAILED: {name}", file=sys.stderr)
                return r.returncode
    return 0


if __name__ == "__main__":
    ap = argparse.ArgumentParser(description="Apply the Hermes cron registry")
    ap.add_argument("--dry-run", action="store_true")
    sys.exit(apply(ap.parse_args().dry_run))
