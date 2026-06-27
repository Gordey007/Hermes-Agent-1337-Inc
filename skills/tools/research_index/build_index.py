"""Research index builder — turns a pile of research/*.md artifacts into a decision map.

After the researcher has fetched a handful of artifacts (via gh_search / web_docs), this
script scans research/*.md, parses each artifact's Title / URL / Summary / Sub-links, and emits:

  research/_index.json   compact machine index [{seq,path,title,url,summary,sub_links,verdict,reason}]
  research/_notes.md      human map: one block per artifact with a `useful` / `skip` verdict

The verdict starts as a heuristic guess (artifacts with a real summary + a known stack signal
lean `useful`; near-empty ones lean `skip`) that the researcher then confirms/overrides — this
is the `research/_notes.md` "what to read / what to ignore" map the architect relies on. It also
surfaces the union of still-unfollowed Sub-links as the next research hops.
"""
from __future__ import annotations

import argparse
import json
import os
import re
from pathlib import Path

STACK_SIGNALS = ("python", "fastapi", "flask", "django", "next.js", "react",
                 "typescript", "stripe", "docker", "postgres", "sqlite", "redis", "llm")


def _section(body: str, header: str) -> str:
    m = re.search(rf"^##\s+{re.escape(header)}\s*\n(.*?)(?=^##\s|\Z)", body, re.M | re.S)
    return m.group(1).strip() if m else ""


def _parse(path: Path) -> dict:
    body = path.read_text(encoding="utf-8", errors="replace")
    title_m = re.search(r"^#\s+(.+)$", body, re.M)
    url_m = re.search(r"\*\*URL:\*\*\s*(\S+)", body)
    summary = _section(body, "Summary")
    sub_raw = _section(body, "Sub-links")
    sub_links = re.findall(r"\[([^\]]+)\]\((https?://[^)]+)\)", sub_raw)
    seq_m = re.match(r"(\d+)_", path.name)

    text = (title_m.group(1) if title_m else "") + " " + summary
    has_signal = any(s in text.lower() for s in STACK_SIGNALS)
    substantive = len(summary) >= 60
    useful = has_signal and substantive
    return {
        "seq": int(seq_m.group(1)) if seq_m else 0,
        "path": str(path),
        "title": title_m.group(1).strip() if title_m else path.stem,
        "url": url_m.group(1) if url_m else "",
        "summary": summary,
        "sub_links": [{"anchor": a, "url": u} for a, u in sub_links],
        "verdict": "useful" if useful else "skip",
        "reason": ("stack signal + real summary" if useful else
                   "thin summary / no stack signal — confirm or drop"),
    }


def build(out_dir: str) -> dict:
    out = Path(out_dir)
    artifacts = sorted(p for p in out.glob("*.md") if not p.name.startswith("_"))
    items = [_parse(p) for p in artifacts]
    items.sort(key=lambda x: x["seq"])

    followed = {it["url"] for it in items}
    next_hops, seen = [], set()
    for it in items:
        for link in it["sub_links"]:
            u = link["url"]
            if u not in followed and u not in seen:
                seen.add(u)
                next_hops.append(link)

    (out / "_index.json").write_text(
        json.dumps({"items": items, "next_hops": next_hops}, ensure_ascii=False, indent=2),
        encoding="utf-8")

    lines = ["# Research notes — usefulness map", "",
             "> Auto-prefilled verdicts; the researcher confirms/overrides each.", ""]
    for it in items:
        mark = "✅" if it["verdict"] == "useful" else "⏭️"
        lines += [f"## {mark} {it['seq']:02d}. {it['title']}  (`{it['verdict']}`)",
                  f"- URL: {it['url']}",
                  f"- Why: {it['reason']}",
                  f"- Summary: {it['summary'][:200] or '_(none)_'}", ""]
    if next_hops:
        lines += ["## Next hops (unfollowed sub-links)", ""]
        lines += [f"- [{l['anchor']}]({l['url']})" for l in next_hops[:20]]
        lines.append("")
    (out / "_notes.md").write_text("\n".join(lines), encoding="utf-8")

    return {"artifacts": len(items),
            "useful": sum(it["verdict"] == "useful" for it in items),
            "skip": sum(it["verdict"] == "skip" for it in items),
            "next_hops": len(next_hops),
            "notes": str(out / "_notes.md"), "index": str(out / "_index.json")}


def main() -> None:
    p = argparse.ArgumentParser(description="Build research/_notes.md + _index.json from artifacts")
    p.add_argument("--out", default=os.getenv("RESEARCH_DIR", "research"),
                   help="research directory to scan")
    args = p.parse_args()
    print(json.dumps(build(args.out), ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
