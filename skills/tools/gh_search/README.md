# gh_search — GitHub smart-search tool

A research CLI tool (not a Hermes skill). It searches for references on GitHub and the web, **cleans
the context**, writes a fixed-structure artifact to `research/`, and prints a
**compact JSON index** to stdout — the researcher reads the index (Summary + Sub-links), not the raw content.

## Why

~50% of a sprint's success is good references. The tool saves the agent's context: instead of raw HTML
the agent gets `{path, title, url, summary, sub_links[]}` and decides the next step.

## Installing dependencies

```bash
pip install httpx trafilatura beautifulsoup4   # already in pyproject.toml
export GITHUB_TOKEN="ghp_..."                   # see env.example
```

## Subcommands

```bash
# 1. Find reference repositories (sort=stars)
python gh_search.py search-repos --query "stripe checkout fastapi" --limit 5 --out research

# 2. Find specific files by code
python gh_search.py search-code --query "create_checkout_session language:python" --limit 5 --out research

# 3. Fetch and clean a page/file (raw, contents API, or doc URL)
python gh_search.py fetch-clean --url https://raw.githubusercontent.com/o/r/HEAD/app.py --terms stripe,checkout --out research
```

## Artifact `research/<NN>_<slug>.md`

Fixed structure (this is the contract for the architect):

```markdown
# <Title>
- **URL:** <link>
- **Meta:** stars: ... | language: ...

## Sub-links
- [anchor](url)        ← starting points for the next search iteration

## Summary
<a 3–6 line digest: what it is, stack/pattern, why it's useful>

## Cleaned content
<cleaned markdown / truncated code>
```

## What gets printed to stdout

A JSON array of compact records (without the full content):

```json
[{"path": "research/03_o-r.md", "title": "o/r", "url": "...", "summary": "...", "sub_links": [{"anchor": "...", "url": "..."}]}]
```

## Context cleaning (`clean.py`)

- HTML → `trafilatura.extract(output_format='markdown', favor_precision=True)` + BeautifulSoup
  pre-cleaning (removing `script/style/nav/footer/aside/header`).
- Code — as is, but truncated around matches with `--terms`, no binaries/lock/minified files,
  limited by `MAX_CONTENT_CHARS`.
- **Sub-links** — outbound links with anchors (filtering social/badges/images), top 12.
- **Summary** — heuristic: the first meaningful paragraph + stack signals + meta.

## Rate limit and cache

- Serialized requests (not concurrent), backoff based on `retry-after` / `x-ratelimit-reset`.
- `code_search` — a separate bucket (~10/window): spend it sparingly.
- ETag cache (`cache.py`, `.gh_cache/`): a repeat sends `If-None-Match`, and on a 304 takes the cache.
  TTL from `GH_CACHE_TTL` (6 h by default).

## How the researcher uses it

Via the `rs-github-search` / `github-research` skill: ≤10 requests per sprint, iteratively —
index → reading Summary+Sub-links → the next `search-*`/`fetch-clean` on the found terms →
a usefulness note in `research/_notes.md`. See `docs/09_github_research.md`.
