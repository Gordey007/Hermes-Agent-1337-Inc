"""Official-docs fetcher — the non-GitHub half of research.

Where gh_search mines open-source repos, this script pulls *official documentation*
(framework guides, API references, changelogs) into the same research/ artifact format so
the architect can read references uniformly.

Subcommands:
  fetch  --url <doc-url> [--terms a,b] [--out DIR]      one page → one artifact
  crawl  --url <doc-url> [--depth 1] [--max 6] [--out DIR]
         one page + a shallow same-host follow of its sub-links (next research hops)

It reuses gh_search's clean.py (trafilatura → markdown + sub-links + summary) and the same
write_artifact layout, then prints a COMPACT JSON index to stdout — the researcher reads the
index (Summary + Sub-links), never the raw HTML.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from urllib.parse import urlparse

import httpx

# clean.py + write_artifact live next to gh_search.py — reuse them so research/ stays uniform.
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "gh_search"))
import clean  # noqa: E402
from gh_search import write_artifact  # noqa: E402

UA = {"User-Agent": "hab-web-docs", "Accept": "text/html,application/xhtml+xml"}


def _fetch_one(url: str, out_dir: str, terms: list[str]) -> dict:
    resp = httpx.get(url, headers=UA, follow_redirects=True, timeout=30)
    text = resp.text
    title = url.rstrip("/").rsplit("/", 1)[-1] or urlparse(url).netloc
    is_html = "<html" in text[:2000].lower() or "text/html" in resp.headers.get("content-type", "")
    if is_html:
        m = re.search(r"<title[^>]*>(.*?)</title>", text, re.I | re.S)
        if m:
            title = " ".join(m.group(1).split())[:120]
        cleaned = clean.html_to_markdown(text)
        sub_links = clean.extract_sub_links(text, url)
    else:
        cleaned = clean.trim_code(text, terms)
        sub_links = []
    summary = clean.summarize(cleaned, title=title)
    return write_artifact(out_dir, title, url, summary, sub_links, cleaned, {"source": "docs", "url": url})


def cmd_fetch(args) -> list[dict]:
    terms = [t for t in (args.terms or "").split(",") if t]
    return [_fetch_one(args.url, args.out, terms)]


def cmd_crawl(args) -> list[dict]:
    """Shallow same-host crawl: fetch the seed, then follow up to --max of its sub-links one
    level deep. Stays on the seed's host so we don't wander off into unrelated sites."""
    terms = [t for t in (args.terms or "").split(",") if t]
    host = urlparse(args.url).netloc
    index = [_fetch_one(args.url, args.out, terms)]
    seen = {args.url}
    if args.depth >= 1:
        for link in index[0]["sub_links"][: args.max]:
            u = link["url"]
            if u in seen or urlparse(u).netloc != host:
                continue
            seen.add(u)
            try:
                index.append(_fetch_one(u, args.out, terms))
            except httpx.HTTPError as e:
                print(f"[web-docs] skip {u}: {e}", file=sys.stderr)
    return index


def main() -> None:
    import os

    p = argparse.ArgumentParser(description="Official-docs fetcher (research/ artifacts)")
    p.add_argument("--out", default=os.getenv("RESEARCH_DIR", "research"),
                   help="artifact directory (research/)")
    sub = p.add_subparsers(dest="cmd", required=True)

    f = sub.add_parser("fetch"); f.add_argument("--url", required=True); f.add_argument("--terms", default=""); f.set_defaults(func=cmd_fetch)
    c = sub.add_parser("crawl"); c.add_argument("--url", required=True); c.add_argument("--terms", default=""); c.add_argument("--depth", type=int, default=1); c.add_argument("--max", type=int, default=6); c.set_defaults(func=cmd_crawl)

    args = p.parse_args()
    index = args.func(args)
    # stdout = a compact index (for the researcher's skill), NOT the full content
    print(json.dumps(index, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
