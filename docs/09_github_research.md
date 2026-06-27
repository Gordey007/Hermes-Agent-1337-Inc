# 09 — GitHub smart-search (the core of research, 50% of success)

A combination of a **TOOL** (`tools/gh_search/`, a real python script) + a **SKILL** (`rs-github-search`, how the researcher uses it). Context cleaning is mandatory.

## Tool: `tools/gh_search/`
A CLI (`search-repos`, `search-code`, `fetch-clean`), stdlib + httpx. Uses `GITHUB_TOKEN`.

1. **Search** via the GitHub REST API:
   - `GET /search/repositories?q=...&sort=stars` — reference repositories.
   - `GET /search/code?q=...` — specific files by code.
   - Serialized requests (not concurrent), backoff by `x-ratelimit-reset`/`retry-after`, a separate `code_search` bucket (≈10/window). Headers `Authorization: Bearer`, `Accept: application/vnd.github+json`.
2. **Read** a file via `raw.githubusercontent.com` or `GET /repos/{o}/{r}/contents/{path}` (base64).
3. **Context cleaning (mandatory):**
   - README/markdown/issues → `trafilatura.extract(html, output_format='markdown', favor_precision=True, include_comments=False)` (BeautifulSoup pre-cleaning: remove `script/style/nav/footer/aside`).
   - Code — as is, trimmed to the relevant fragments (around the matches), without binaries/minified/lock files, with a size limit per file.
   - **Sub-links:** from the cleaned page, gather outgoing links (markdown links, repo files, doc sections, mentioned repositories) → normalize, deduplicate, filter out junk → top-N with anchor text. These are the "next entry points".
   - **Summary:** a 3–6 line digest (what it is, stack/pattern, why it's useful).
4. **Artifact** `research/<NN>_<slug>.md` — a fixed structure: **Title** / **URL** / **Sub-links** / **Summary** / **Cleaned content**.
5. **Return to the researcher** — NOT the whole content, but a compact JSON index `{path, title, url, summary, sub_links[]}` on stdout. The full content — only in the file.
6. Cache by `etag`/request key.

Files: `gh_search.py`, `clean.py`, `cache.py`, `README.md`.

## Skill: iterative loop (researcher)
- **≤10 requests/sprint** (the `github_search` counter in kanban).
- Loop: request → the tool writes the artifact + returns the index → the researcher **reads ONLY the Summary + Sub-links** (not the whole content) → based on them forms the next request (drill into a sub-link via `fetch-clean` or a new `search-*`) → a note in `research/_notes.md` (`useful` + what's valuable / `skip` + why).
- Stop: enough references (`rs-decide-enough`) OR the limit of 10.
- Result: a set of `research/NN_*.md` + `research/_notes.md` (a map of what's useful) → input for the architect.
