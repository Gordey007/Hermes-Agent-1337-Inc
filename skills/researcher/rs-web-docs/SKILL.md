---
name: rs-web-docs
description: Find and clean official documentation (Python/Next.js/libraries).
version: 1.0.0
author: hermes-team
license: MIT
metadata:
  hermes:
    requires_toolsets: [shell, python]
---

# rs-web-docs

## WHO
researcher.

## WHEN
- You need a canonical API/config reference better taken from official documentation than from a repository.

## STEPS
1. Determine the official documentation domain (docs.python.org, nextjs.org, *.readthedocs.io, developer.mozilla.org) — within policy.
2. Fetch + clean one page:
   `python skills/tools/web_docs/web_docs.py fetch --url "<doc-url>" --terms "<a,b>" --out "<research_dir>"`.
   To pull a section plus its sub-pages one level deep (same host):
   `python skills/tools/web_docs/web_docs.py crawl --url "<doc-url>" --depth 1 --max 6 --out "<research_dir>"`.
3. The tool reuses gh_search's cleaner (trafilatura+precision), writes the artifact
   `research/<NN>_<slug>.md` (Title/URL/Sub-links/Summary/Cleaned), and prints a COMPACT JSON
   index `{path,title,url,summary,sub_links[]}` to stdout.
4. Read ONLY `summary` + `sub_links` from the index (not the entire Cleaned content).

## OUTPUT
- A documentation artifact in `research/` + a compact index.

## NEXT
- `rs-clean-context` (ensure cleaning) → `rs-write-notes`.

## LIMITS
- Only domains from policy. Do not pull whole pages in full — only the cleaned relevant sections.
