"""Template-based sprint scaffolder.

`og-start-sprint` calls this to GENERATE a sprint's program from templates/ rather than
hand-writing it. Given a tweet and sprint number, it materializes the Karpathy three-file
contract plus a runnable iteration program into the sprint directory:

    <sprint_dir>/
      program.md          # IMMUTABLE direction (Karpathy program.md)   ← templates/program.md.tmpl
      dod.json            # IMMUTABLE Definition of Done                ← templates/dod.json.tmpl
      run_sprint.py       # the iteration harness (outer/inner loops)   ← templates/run_sprint.py.tmpl
      product/
        README.md         # product skeleton                           ← templates/product_readme.md.tmpl
        backend/          # (empty, the developer fills it)
      research/  design/  reports/

All names come from infra/naming.py, so the generated program is consistent with the rest of
the pipeline (docker project, compose path, MinIO keys). Re-running is idempotent for the
contract files; existing product/ content is never overwritten.

Usage:
    uv run 03_auto_research/scaffold.py --tweet 2070653124969193883 --sprint 1 \
        --direction "I need a tiny Flask API that ..." [--dod-from-tweet] [--root /sandbox]
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path
from string import Template

HERE = Path(__file__).resolve().parent
TEMPLATES = HERE / "templates"
# infra/naming.py is the single source of names.
sys.path.insert(0, str(HERE.parent / "infra"))
import naming  # noqa: E402

MAX_INNER = 10
MAX_OUTER = 10


def _render(tmpl_name: str, mapping: dict) -> str:
    text = (TEMPLATES / tmpl_name).read_text(encoding="utf-8")
    # safe_substitute: leave unknown ${...} (e.g. JSON cmd escapes) untouched.
    return Template(text).safe_substitute(mapping)


def scaffold(tweet_id: str, sprint: int, direction: str, root: str = "/sandbox") -> dict:
    # naming.* return absolute /sandbox paths; allow a --root override for local runs.
    def localize(p: str) -> Path:
        return Path(root) / Path(p).relative_to("/sandbox") if p.startswith("/sandbox") else Path(p)

    sprint_dir = localize(naming.sprint_dir(tweet_id, sprint))
    product = localize(naming.product_dir(tweet_id, sprint))
    compose_path = naming.compose_path(tweet_id, sprint)
    docker_project = naming.docker_project(tweet_id, sprint)

    for sub in (sprint_dir, product / "backend", sprint_dir / "research",
                sprint_dir / "design", sprint_dir / "reports"):
        sub.mkdir(parents=True, exist_ok=True)

    mapping = {
        "TWEETID": str(tweet_id),
        "SPRINT": str(sprint),
        "DIRECTION": direction.strip(),
        "SPRINT_DIR": str(sprint_dir),
        "PRODUCT_DIR": str(product),
        "DOD_PATH": str(sprint_dir / "dod.json"),
        "DOCKER_PROJECT": docker_project,
        "COMPOSE_PATH": compose_path,
        "ENGINE_DIR": str(HERE),
        "MAX_INNER": str(MAX_INNER),
        "MAX_OUTER": str(MAX_OUTER),
    }

    written = []
    # IMMUTABLE contract files: write once, never clobber an existing sprint.
    for tmpl, target in (("program.md.tmpl", sprint_dir / "program.md"),
                         ("dod.json.tmpl", sprint_dir / "dod.json"),
                         ("product_readme.md.tmpl", product / "README.md")):
        if not target.exists():
            target.write_text(_render(tmpl, mapping), encoding="utf-8")
            written.append(str(target))

    # the iteration program is always regenerated (it is derived, not authored).
    run_prog = sprint_dir / "run_sprint.py"
    run_prog.write_text(_render("run_sprint.py.tmpl", mapping), encoding="utf-8")
    written.append(str(run_prog))

    return {"sprint_dir": str(sprint_dir), "run_program": str(run_prog),
            "dod": mapping["DOD_PATH"], "docker_project": docker_project,
            "compose_path": compose_path, "written": written}


if __name__ == "__main__":
    import json

    ap = argparse.ArgumentParser(description="Generate a sprint program from templates")
    ap.add_argument("--tweet", required=True)
    ap.add_argument("--sprint", type=int, default=1)
    ap.add_argument("--direction", required=True, help="the lead/tweet text = the goal")
    ap.add_argument("--root", default="/sandbox", help="filesystem root (override for local runs)")
    ap.add_argument("--dod-from-tweet", action="store_true",
                    help="reserved: let the architect expand dod.json from the direction")
    args = ap.parse_args()
    out = scaffold(args.tweet, args.sprint, args.direction, args.root)
    print(json.dumps(out, ensure_ascii=False, indent=2))
