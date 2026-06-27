#!/usr/bin/env python3
"""skill_evolve.py — memory-driven self-improvement of SKILL.md files.

A profile does not rewrite its skills by guesswork. During work it RECORDS lessons
(what worked / what failed) into an append-only memory log; later (usually at sprint
teardown, driven by the evaluator) it PROPOSES an improvement from the accumulated
lessons and BUMPS the skill to a new version — keeping the old one archived so history
is never lost.

Memory store (append-only JSONL), one lesson per line:
    {ts, skill, profile, sprint, outcome: worked|failed, lesson, evidence}
Default path: $HERMES_MEMORY_DIR/lessons.jsonl  (fallback ./memory/lessons.jsonl).
This is the same knowledge that survives a sprint via reports/ → MinIO hermes-reports/.

Commands (all print compact JSON to stdout; never raw file bodies into context):
    record   --skill <name> --profile <p> --outcome worked|failed --lesson "..."
             [--sprint <id>] [--evidence "..."]
    lessons  --skill <name> [--limit N]                 → relevant lessons, newest first
    propose  --skill-path <dir-or-SKILL.md>             → {version, worked[], failed[], hint}
    bump     --skill-path <dir-or-SKILL.md> --changelog "..." [--body-file F | stdin]
             → archives the old version, writes a new SKILL.md with version+0.1 and a
               Changelog entry; prints {old_version, new_version, archived}.

Versioning: semver, minor bump (x.Y.z → x.(Y+1).0). Old file copied to
    <skill-dir>/versions/SKILL.v<old>.md
so every improvement is auditable and roll-back-able.
"""
from __future__ import annotations

import argparse
import datetime as _dt
import json
import os
import re
import shutil
import sys
from pathlib import Path

# Windows consoles default to cp1252 and choke on em-dashes / cyrillic paths in our JSON.
for _stream in (sys.stdout, sys.stderr):
    try:
        _stream.reconfigure(encoding="utf-8")  # type: ignore[attr-defined]
    except (AttributeError, ValueError):
        pass


def _memory_path() -> Path:
    root = Path(os.getenv("HERMES_MEMORY_DIR", "memory"))
    root.mkdir(parents=True, exist_ok=True)
    return root / "lessons.jsonl"


def _now() -> str:
    return _dt.datetime.now(_dt.timezone.utc).isoformat(timespec="seconds")


def _resolve_skill(path: str) -> Path:
    p = Path(path)
    if p.is_dir():
        p = p / "SKILL.md"
    if not p.exists():
        raise FileNotFoundError(f"SKILL.md not found at {p}")
    return p


def _read_lessons(skill: str | None = None) -> list[dict]:
    mp = _memory_path()
    if not mp.exists():
        return []
    out = []
    for line in mp.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            row = json.loads(line)
        except ValueError:
            continue
        if skill is None or row.get("skill") == skill:
            out.append(row)
    return out


_FRONT_VERSION = re.compile(r"^(version:\s*)(\d+)\.(\d+)\.(\d+)\s*$", re.MULTILINE)


def _get_version(text: str) -> tuple[int, int, int]:
    m = _FRONT_VERSION.search(text)
    if not m:
        return (1, 0, 0)
    return int(m.group(2)), int(m.group(3)), int(m.group(4))


# ---- commands ---------------------------------------------------------------

def cmd_record(a) -> dict:
    mp = _memory_path()
    row = {
        "ts": _now(),
        "skill": a.skill,
        "profile": a.profile,
        "sprint": a.sprint,
        "outcome": a.outcome,
        "lesson": a.lesson,
        "evidence": a.evidence,
    }
    with mp.open("a", encoding="utf-8") as f:
        f.write(json.dumps(row, ensure_ascii=False) + "\n")
    return {"ok": True, "skill": a.skill, "stored_at": str(mp),
            "total_for_skill": len(_read_lessons(a.skill))}


def cmd_lessons(a) -> dict:
    rows = _read_lessons(a.skill)
    rows.sort(key=lambda r: r.get("ts", ""), reverse=True)
    if a.limit:
        rows = rows[: a.limit]
    return {"skill": a.skill, "count": len(rows), "lessons": rows}


def cmd_propose(a) -> dict:
    skill_file = _resolve_skill(a.skill_path)
    name = skill_file.parent.name
    text = skill_file.read_text(encoding="utf-8")
    ver = ".".join(map(str, _get_version(text)))
    rows = _read_lessons(name)
    worked = [r["lesson"] for r in rows if r.get("outcome") == "worked"]
    failed = [r["lesson"] for r in rows if r.get("outcome") == "failed"]
    hint = ("Encode the 'worked' lessons as explicit STEPS and the 'failed' ones as LIMITS/"
            "guardrails, then call `bump` with the rewritten body." if rows
            else "No lessons recorded yet — keep using the skill and `record` outcomes first.")
    return {"skill": name, "path": str(skill_file), "version": ver,
            "lessons_total": len(rows), "worked": worked, "failed": failed, "hint": hint}


def cmd_bump(a) -> dict:
    skill_file = _resolve_skill(a.skill_path)
    name = skill_file.parent.name
    old_text = skill_file.read_text(encoding="utf-8")
    maj, minr, _ = _get_version(old_text)
    old_ver = f"{maj}.{minr}.0" if _FRONT_VERSION.search(old_text) else "1.0.0"
    new_ver = f"{maj}.{minr + 1}.0"

    # archive the old version
    vdir = skill_file.parent / "versions"
    vdir.mkdir(exist_ok=True)
    archived = vdir / f"SKILL.v{old_ver}.md"
    shutil.copy2(skill_file, archived)

    # new body: from --body-file, stdin, or reuse old text (version-only bump)
    if a.body_file:
        new_body = Path(a.body_file).read_text(encoding="utf-8")
    elif not sys.stdin.isatty():
        new_body = sys.stdin.read()
    else:
        new_body = old_text
    if not new_body.strip():
        new_body = old_text

    # set the new version in frontmatter
    if _FRONT_VERSION.search(new_body):
        new_body = _FRONT_VERSION.sub(rf"\g<1>{new_ver}", new_body, count=1)

    # append a changelog line
    stamp = _now()
    entry = f"- v{new_ver} ({stamp[:10]}): {a.changelog}"
    if "## Changelog" in new_body:
        new_body = new_body.replace("## Changelog\n", f"## Changelog\n{entry}\n", 1)
    else:
        new_body = new_body.rstrip() + f"\n\n## Changelog\n{entry}\n"

    skill_file.write_text(new_body, encoding="utf-8")

    # record the evolution itself as a lesson
    with _memory_path().open("a", encoding="utf-8") as f:
        f.write(json.dumps({"ts": stamp, "skill": name, "profile": a.profile,
                            "sprint": a.sprint, "outcome": "evolved",
                            "lesson": a.changelog,
                            "evidence": f"{old_ver}->{new_ver}"}, ensure_ascii=False) + "\n")

    return {"ok": True, "skill": name, "old_version": old_ver, "new_version": new_ver,
            "archived": str(archived), "path": str(skill_file)}


def main() -> None:
    ap = argparse.ArgumentParser(description="Memory-driven SKILL.md self-improvement")
    sub = ap.add_subparsers(dest="cmd", required=True)

    r = sub.add_parser("record", help="append a lesson to memory")
    r.add_argument("--skill", required=True)
    r.add_argument("--profile", default="unknown")
    r.add_argument("--outcome", required=True, choices=["worked", "failed"])
    r.add_argument("--lesson", required=True)
    r.add_argument("--sprint", default=None)
    r.add_argument("--evidence", default=None)
    r.set_defaults(fn=cmd_record)

    l = sub.add_parser("lessons", help="list lessons for a skill")
    l.add_argument("--skill", required=True)
    l.add_argument("--limit", type=int, default=0)
    l.set_defaults(fn=cmd_lessons)

    p = sub.add_parser("propose", help="summarize lessons into an improvement brief")
    p.add_argument("--skill-path", required=True)
    p.set_defaults(fn=cmd_propose)

    b = sub.add_parser("bump", help="write a new versioned SKILL.md (archives the old)")
    b.add_argument("--skill-path", required=True)
    b.add_argument("--changelog", required=True)
    b.add_argument("--body-file", default=None, help="new body file; else stdin; else version-only")
    b.add_argument("--profile", default="unknown")
    b.add_argument("--sprint", default=None)
    b.set_defaults(fn=cmd_bump)

    args = ap.parse_args()
    try:
        out = args.fn(args)
    except Exception as e:  # noqa: BLE001 — surface a clean JSON error + nonzero exit
        print(json.dumps({"error": str(e)}, ensure_ascii=False), file=sys.stderr)
        sys.exit(1)
    print(json.dumps(out, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
