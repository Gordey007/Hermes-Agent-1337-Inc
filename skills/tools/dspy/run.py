"""Run a DSPy program by name on JSON input and print JSON output.

This is THE tool boundary: every agent/skill calls DSPy through this CLI, never by
importing dspy directly. It loads the compiled (optimized) program if compiled/<name>.json
exists, otherwise the zero-shot version — callers don't care which.

Convention (matches the other tools in skills/tools/): read JSON, write compact JSON to
stdout; nothing else on stdout. Errors go to stderr + non-zero exit.

Usage:
    echo '{"tweet_text":"I will pay for a tiny CSV->chart tool"}' \
        | uv run skills/tools/dspy/run.py --name qualify_lead

    uv run skills/tools/dspy/run.py --name qualify_lead \
        --input '{"tweet_text":"..."}'

    uv run skills/tools/dspy/run.py --list
"""
from __future__ import annotations

import argparse
import json
import sys

import lm as lm_mod
import programs as programs_mod


def run(name: str, payload: dict) -> dict:
    lm_mod.configure()
    program = programs_mod.load(name)
    pred = program(**payload)
    # dspy.Prediction → plain dict of its output fields (skip private/reasoning unless asked).
    out = {k: v for k, v in pred.items()} if hasattr(pred, "items") else dict(pred.__dict__)
    out = {k: v for k, v in out.items() if not k.startswith("_")}
    return out


def main() -> int:
    ap = argparse.ArgumentParser(description="Run a DSPy program on JSON input")
    ap.add_argument("--name", help="program name (see --list)")
    ap.add_argument("--input", help="JSON input; if omitted, read stdin")
    ap.add_argument("--list", action="store_true", help="list available programs and exit")
    args = ap.parse_args()

    if args.list:
        print(json.dumps({"programs": programs_mod.list_programs()}, ensure_ascii=False))
        return 0

    if not args.name:
        print("error: --name is required (or use --list)", file=sys.stderr)
        return 2

    raw = args.input if args.input is not None else sys.stdin.read()
    try:
        payload = json.loads(raw) if raw.strip() else {}
    except json.JSONDecodeError as e:
        print(f"error: invalid JSON input: {e}", file=sys.stderr)
        return 2

    try:
        out = run(args.name, payload)
    except Exception as e:  # surface a clean error to the calling skill
        print(f"error: {type(e).__name__}: {e}", file=sys.stderr)
        return 1

    print(json.dumps(out, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
