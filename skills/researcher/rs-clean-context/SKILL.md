---
name: rs-clean-context
description: Guarantee content cleaning (trafilatura+precision) before writing the artifact.
version: 1.0.0
author: hermes-team
license: MIT
metadata:
  hermes:
    requires_toolsets: [python]
---

# rs-clean-context

## WHO
researcher.

## WHEN
- Before committing any web/markdown artifact to `research/`.

## STEPS
1. Make sure the content went through the `clean.py` tool: `trafilatura.extract(html, output_format='markdown',
   favor_precision=True, include_comments=False)` + BeautifulSoup pre-cleaning (strip `script/style/nav/footer/aside`).
2. Code — keep as is, but trim to the relevant fragments (around the matches); no binaries/minified/lock files; cap the size per file.
3. Verify that the artifact has Sub-links filled in (normalized, deduplicated, no badges/social) and a Summary (3–6 lines).

## OUTPUT
- A cleaned, compact artifact `research/<NN>_*.md` with no clutter.

## NEXT
- `rs-write-notes` (record usefulness).

## LIMITS
- Do not save raw HTML/minified/binaries. Cleaning is mandatory — saving context is critical.
