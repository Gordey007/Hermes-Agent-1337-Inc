"""Context cleaning: HTML/markdown → clean markdown, sub-link extraction and a summary.

A required part of research: the researcher must not bloat its context with raw HTML.
- HTML → trafilatura.extract(output_format='markdown', favor_precision=True) with a BS4 pre-clean.
- Code — as is, but truncated around relevant fragments, no binaries/lock/minified.
- Sub-links — outbound links (entry points for the next search iteration).
- Summary — a 3-6 line heuristic digest.
"""
from __future__ import annotations

import re
from urllib.parse import urldefrag, urljoin, urlparse

import trafilatura
from bs4 import BeautifulSoup

MAX_CONTENT_CHARS = 16000
MAX_SUB_LINKS = 12
_JUNK_HOSTS = {"twitter.com", "x.com", "facebook.com", "linkedin.com", "youtube.com",
               "discord.gg", "discord.com", "t.me", "instagram.com"}
_JUNK_PATTERNS = re.compile(r"(badge|shields\.io|sponsor|/stargazers|/watchers|/forks|"
                            r"\.svg|\.png|\.gif|\.jpg)", re.I)


def _strip_html(html: str) -> str:
    if BeautifulSoup is None:
        return html
    soup = BeautifulSoup(html, "html.parser")
    for tag in soup(["script", "style", "nav", "footer", "aside", "header", "noscript", "svg"]):
        tag.decompose()
    return str(soup)


def html_to_markdown(html: str) -> str:
    pre = _strip_html(html)
    if trafilatura is not None:
        md = trafilatura.extract(pre, output_format="markdown",
                                 favor_precision=True, include_comments=False,
                                 include_tables=True)
        if md:
            return md.strip()
    # fallback path: crude text extraction
    if BeautifulSoup is not None:
        return BeautifulSoup(pre, "html.parser").get_text("\n", strip=True)
    return re.sub(r"<[^>]+>", "", pre)


def extract_sub_links(html: str, base_url: str) -> list[dict]:
    """Collect outbound links with anchors: entry points for the next search iteration."""
    if BeautifulSoup is None:
        return []
    soup = BeautifulSoup(html, "html.parser")
    seen: set[str] = set()
    links: list[dict] = []
    for a in soup.find_all("a", href=True):
        href = urldefrag(urljoin(base_url, a["href"]))[0]
        anchor = " ".join(a.get_text(" ", strip=True).split())
        if not href.startswith("http"):
            continue
        host = urlparse(href).netloc.lower()
        if host in _JUNK_HOSTS or _JUNK_PATTERNS.search(href):
            continue
        if not anchor or len(anchor) < 3:
            continue
        if href in seen:
            continue
        seen.add(href)
        links.append({"url": href, "anchor": anchor[:80]})
        if len(links) >= MAX_SUB_LINKS:
            break
    return links


def summarize(markdown: str, title: str = "", meta: dict | None = None) -> str:
    """Heuristic 3-6 line digest: the first meaningful paragraph + stack signals."""
    meta = meta or {}
    text = re.sub(r"\s+", " ", re.sub(r"[#*`>\-]", " ", markdown)).strip()
    first = text[:400]
    stack_hits = sorted({kw for kw in (
        "python", "fastapi", "django", "flask", "next.js", "react", "typescript",
        "stripe", "docker", "postgres", "sqlite", "redis", "openai", "llm",
    ) if kw in markdown.lower()})
    lines = []
    if title:
        lines.append(f"What it is: {title}.")
    if first:
        lines.append(f"Gist: {first.strip()}")
    if stack_hits:
        lines.append(f"Stack/patterns: {', '.join(stack_hits)}.")
    if meta.get("stars") is not None:
        lines.append(f"Stars: {meta['stars']}, language: {meta.get('language', '?')}.")
    return "\n".join(lines[:6])


def trim_code(code: str, query_terms: list[str] | None = None) -> str:
    """Trim code: if there are term matches, return windows around them, otherwise the head."""
    if len(code) <= MAX_CONTENT_CHARS:
        return code
    if query_terms:
        lines = code.splitlines()
        keep: set[int] = set()
        low_terms = [t.lower() for t in query_terms if t]
        for i, ln in enumerate(lines):
            if any(t in ln.lower() for t in low_terms):
                keep.update(range(max(0, i - 8), min(len(lines), i + 9)))
        if keep:
            out, prev = [], -2
            for i in sorted(keep):
                if i != prev + 1:
                    out.append("...")
                out.append(lines[i])
                prev = i
            joined = "\n".join(out)
            if joined:
                return joined[:MAX_CONTENT_CHARS]
    return code[:MAX_CONTENT_CHARS] + "\n... [truncated]"
