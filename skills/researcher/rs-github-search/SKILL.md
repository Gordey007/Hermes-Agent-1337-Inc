---
name: rs-github-search
description: Run the GitHub smart-search tool (tools/gh_search), build a query, read the index.
version: 1.0.0
author: hermes-team
license: MIT
metadata:
  hermes:
    requires_toolsets: [shell, python]
---

# rs-github-search

## WHO
researcher.

## WHEN
- There's a topic from `research/_plan.md`, the `github_search` limit is not exhausted (<10).

## STEPS
1. Build a query from the topic (stack/pattern terms).
2. Call the tool: `python skills/tools/gh_search/gh_search.py search-repos --query "<q>"` or `search-code --query "<q>"`;
   to dig into a result — `fetch-clean --url "<url>"`.
3. The tool writes the artifact `research/<NN>_<slug>.md` (Title/URL/Sub-links/Summary/Cleaned) and prints to stdout
   a COMPACT JSON index `{path,title,url,summary,sub_links[]}`.
4. Read ONLY `summary` + `sub_links` from the index (not the entire Cleaned content).
5. Increment the counter: `python 04_team/kanban/counters.py inc --tweet <tweetid> --sprint <N> --counter github_search` (returns `{value,max,over_limit}`).

## OUTPUT
- The artifact `research/<NN>_*.md` (written by the tool) + the compact index read by the researcher.

## NEXT
- `rs-decide-enough` (whether it's enough) → if not, the next query by `sub_links`/new terms (or `rs-web-docs`).

## LIMITS
- ≤10 GitHub queries per sprint. Do not read the full Cleaned into context — only Summary+Sub-links. Respect the tool's backoff.
