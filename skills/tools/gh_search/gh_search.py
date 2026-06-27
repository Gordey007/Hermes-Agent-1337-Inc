"""GitHub smart-search CLI — the core of research (≈50% of a sprint's success).

Subcommands:
  search-repos  --query "..." [--limit N] [--out DIR]
  search-code   --query "..." [--limit N] [--out DIR]
  fetch-clean   --url <github/raw/doc-url> [--terms a,b] [--out DIR]

What it does: search via the GitHub REST API (sort=stars / code), read a file (raw/contents),
clean the context (clean.py: markdown + sub-links + summary), write an ARTIFACT
research/<NN>_<slug>.md with a fixed structure (Title/URL/Sub-links/Summary/Cleaned),
and print a COMPACT JSON index {path,title,url,summary,sub_links[]} to stdout —
the researcher reads the index (Summary+Sub-links), not the whole content.

Features: serialized requests (not concurrent), backoff based on x-ratelimit-reset /
retry-after, separate accounting for the code_search bucket, an ETag cache, a Bearer token from GITHUB_TOKEN.
"""
from __future__ import annotations

import argparse
import base64
import json
import os
import re
import sys
import time
from pathlib import Path

import httpx

import cache
import clean

API = "https://api.github.com"
TOKEN = os.getenv("GITHUB_TOKEN", "")
HEADERS = {
    "Accept": "application/vnd.github+json",
    "X-GitHub-Api-Version": "2022-11-28",
    "User-Agent": "hab-gh-search",
}
if TOKEN:
    HEADERS["Authorization"] = f"Bearer {TOKEN}"

DEFAULT_OUT = os.getenv("RESEARCH_DIR", "research")


# ----------------------------- HTTP with backoff/cache -----------------------------

def _respect_rate_limit(resp: httpx.Response) -> None:
    if resp.status_code in (403, 429):
        retry = resp.headers.get("retry-after")
        if retry:
            wait = int(retry)
        else:
            reset = resp.headers.get("x-ratelimit-reset")
            wait = max(0, int(reset) - int(time.time())) + 1 if reset else 30
        wait = min(wait, 120)
        print(f"[gh] rate-limited, sleeping {wait}s", file=sys.stderr)
        time.sleep(wait)


def gh_get(url: str, params: dict | None = None, accept: str | None = None) -> httpx.Response:
    raw_key = url + json.dumps(params or {}, sort_keys=True)
    cached = cache.fresh(raw_key)
    if cached:
        resp = httpx.Response(cached["status"], json=cached["payload"])
        resp._content = json.dumps(cached["payload"]).encode() if isinstance(cached["payload"], (dict, list)) else (cached["payload"] or "").encode()
        return resp

    headers = dict(HEADERS)
    if accept:
        headers["Accept"] = accept
    stale = cache.get(raw_key)
    if stale and stale.get("etag"):
        headers["If-None-Match"] = stale["etag"]

    for attempt in range(4):
        with httpx.Client(timeout=30, follow_redirects=True) as client:
            resp = client.get(url, params=params, headers=headers)
        if resp.status_code == 304 and stale:
            payload = stale["payload"]
            r = httpx.Response(200, json=payload) if isinstance(payload, (dict, list)) else httpx.Response(200, text=payload)
            return r
        if resp.status_code in (403, 429):
            _respect_rate_limit(resp)
            continue
        etag = resp.headers.get("etag")
        try:
            payload = resp.json()
        except ValueError:
            payload = resp.text
        if resp.is_success:
            cache.put(raw_key, etag, resp.status_code, payload)
        return resp
    return resp


# ----------------------------- writing the artifact -----------------------------

def _slug(text: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-")[:40] or "item"


def _next_seq(out_dir: Path) -> int:
    out_dir.mkdir(parents=True, exist_ok=True)
    existing = [int(m.group(1)) for f in out_dir.glob("*.md")
                if (m := re.match(r"(\d+)_", f.name))]
    return (max(existing) + 1) if existing else 1


def write_artifact(out_dir: str, title: str, url: str, summary: str,
                   sub_links: list[dict], cleaned: str, meta: dict | None = None) -> dict:
    out = Path(out_dir)
    seq = _next_seq(out)
    path = out / f"{seq:02d}_{_slug(title)}.md"
    meta = meta or {}
    meta_line = " | ".join(f"{k}: {v}" for k, v in meta.items() if v is not None)

    sub_md = "\n".join(f"- [{l['anchor']}]({l['url']})" for l in sub_links) or "_(none)_"
    body = (
        f"# {title}\n\n"
        f"- **URL:** {url}\n"
        + (f"- **Meta:** {meta_line}\n" if meta_line else "")
        + f"\n## Sub-links\n{sub_md}\n\n"
        f"## Summary\n{summary}\n\n"
        f"## Cleaned content\n\n{cleaned}\n"
    )
    path.write_text(body, encoding="utf-8")
    return {"path": str(path), "title": title, "url": url,
            "summary": summary, "sub_links": sub_links}


# ----------------------------- subcommands -----------------------------

def cmd_search_repos(args) -> list[dict]:
    resp = gh_get(f"{API}/search/repositories",
                  {"q": args.query, "sort": "stars", "order": "desc",
                   "per_page": args.limit})
    if not resp.is_success:
        print(f"[gh] search-repos failed: {resp.status_code} {resp.text[:200]}", file=sys.stderr)
        return []
    out_index = []
    for item in resp.json().get("items", [])[:args.limit]:
        title = item["full_name"]
        url = item["html_url"]
        desc = item.get("description") or ""
        meta = {"stars": item.get("stargazers_count"), "language": item.get("language")}
        # a lightweight artifact from the repo card (without downloading the README — via a separate fetch-clean)
        summary = clean.summarize(desc, title=title, meta=meta)
        sub = [{"anchor": "README (fetch-clean)", "url": f"{url}#readme"},
               {"anchor": "repo files", "url": f"{url}/tree/HEAD"}]
        out_index.append(write_artifact(args.out, title, url, summary, sub, desc, meta))
    return out_index


def cmd_search_code(args) -> list[dict]:
    resp = gh_get(f"{API}/search/code", {"q": args.query, "per_page": args.limit},
                  accept="application/vnd.github.text-match+json")
    if not resp.is_success:
        print(f"[gh] search-code failed: {resp.status_code} {resp.text[:200]}", file=sys.stderr)
        return []
    out_index = []
    for item in resp.json().get("items", [])[:args.limit]:
        repo = item["repository"]["full_name"]
        path = item["path"]
        url = item["html_url"]
        title = f"{repo}/{path}"
        fragments = "\n".join(m.get("fragment", "")
                              for m in item.get("text_matches", []))
        meta = {"repo": repo, "path": path}
        summary = clean.summarize(fragments, title=title, meta=meta)
        sub = [{"anchor": "raw file (fetch-clean)",
                "url": f"https://raw.githubusercontent.com/{repo}/HEAD/{path}"}]
        out_index.append(write_artifact(args.out, title, url, summary, sub,
                                        clean.trim_code(fragments), meta))
    return out_index


def cmd_fetch_clean(args) -> list[dict]:
    url = args.url
    terms = [t for t in (args.terms or "").split(",") if t]
    resp = gh_get(url) if "api.github.com" in url else httpx.get(
        url, headers={"User-Agent": "hab-gh-search"}, follow_redirects=True, timeout=30)

    # contents API → base64
    if "api.github.com" in url and isinstance(resp.json() if resp.is_success else None, dict) \
            and resp.json().get("encoding") == "base64":
        content = base64.b64decode(resp.json()["content"]).decode("utf-8", "replace")
        title = resp.json().get("name", url)
        cleaned = clean.trim_code(content, terms)
        sub_links: list[dict] = []
    else:
        text = resp.text
        is_html = "<html" in text[:2000].lower() or "text/html" in resp.headers.get("content-type", "")
        title = url.rsplit("/", 1)[-1] or url
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
    return [write_artifact(args.out, title, url, summary, sub_links, cleaned, {"source": url})]


def main() -> None:
    p = argparse.ArgumentParser(description="GitHub smart-search tool")
    p.add_argument("--out", default=DEFAULT_OUT, help="artifact directory (research/)")
    sub = p.add_subparsers(dest="cmd", required=True)

    sr = sub.add_parser("search-repos"); sr.add_argument("--query", required=True); sr.add_argument("--limit", type=int, default=5); sr.set_defaults(func=cmd_search_repos)
    sc = sub.add_parser("search-code"); sc.add_argument("--query", required=True); sc.add_argument("--limit", type=int, default=5); sc.set_defaults(func=cmd_search_code)
    fc = sub.add_parser("fetch-clean"); fc.add_argument("--url", required=True); fc.add_argument("--terms", default=""); fc.set_defaults(func=cmd_fetch_clean)

    args = p.parse_args()
    index = args.func(args)
    # stdout = a compact index (for the researcher's skill), NOT the full content
    print(json.dumps(index, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
