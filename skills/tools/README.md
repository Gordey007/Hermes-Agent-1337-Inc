# tools/ — the researcher's real scripts

The profiles are not "just skills": the SKILL.md files are thin procedures that drive these
real Python CLIs. The scripts do the heavy lifting (HTTP, cleaning, indexing, DSPy); the skills
decide *when* to call them and *how to read* their output. Every tool prints a compact JSON
result to stdout — never raw content into context.

| Tool | What it does | Driven by skill |
|---|---|---|
| `gh_search/gh_search.py` | Search GitHub repos/code + fetch-clean any URL → `research/<NN>_*.md` | `rs-github-search` |
| `web_docs/web_docs.py` | Fetch/crawl official docs (same cleaner) → `research/<NN>_*.md` | `rs-web-docs` |
| `research_index/build_index.py` | Scan `research/*.md` → `research/_notes.md` + `_index.json` | `rs-write-notes` |
| `dspy/run.py` | Run an optimized DSPy program on JSON → JSON decision (qualify/verdict/offer/…) | `dspy-decide` (see [dspy/README.md](dspy/README.md)) |
| `skill_evolve/skill_evolve.py` | Record lessons to memory, then write a NEW versioned SKILL.md from them (archives the old) | `skill-evolve` |

## The research loop

```
rs-plan-research        → research/_plan.md (topics, stack terms)
   │
   ├── rs-github-search → gh_search.py search-repos/search-code/fetch-clean
   └── rs-web-docs      → web_docs.py fetch/crawl
   │        (both append research/<NN>_<slug>.md, print compact index)
   ▼
rs-write-notes          → build_index.py  (research/_notes.md useful/skip + next_hops)
   ▼
rs-decide-enough        → enough? handoff to architect : loop back (≤10 queries/sprint)
```

`build_index.py` closes the loop: its `next_hops` (unfollowed sub-links) feed the next
`gh_search`/`web_docs` call, and its `useful`/`skip` map is exactly what the architect reads
instead of the raw artifacts.

## Shared cleaner

`web_docs.py` reuses `gh_search/clean.py` (trafilatura + BeautifulSoup pre-clean + sub-link
extraction + heuristic summary) and `gh_search.write_artifact`, so every artifact — GitHub or
docs — has the identical `Title / URL / Sub-links / Summary / Cleaned content` shape.

## Dependencies

```bash
pip install httpx trafilatura beautifulsoup4   # already in pyproject.toml
export GITHUB_TOKEN="ghp_..."                  # gh_search only; see env.example
export RESEARCH_DIR="/sandbox/work/hab_<id>/s<N>/research"   # default: ./research
```
