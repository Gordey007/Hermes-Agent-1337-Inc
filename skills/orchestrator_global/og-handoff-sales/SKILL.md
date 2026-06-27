---
name: og-handoff-sales
description: On dev_status='done', hand the lead off to sales (artifact in MinIO + ready for presigned).
version: 1.0.0
author: hermes-team
license: MIT
metadata:
  hermes:
    requires_toolsets: [sqlite, python]
---

# og-handoff-sales

## WHO
orchestrator_global.

## WHEN
- The sprint finished with a `keep`/`done` verdict; the artifact is already uploaded to MinIO (`ev-push-reports`/outer_loop).

## STEPS
1. Verify that `dev_artifact` (MinIO key `hermes-artifacts/hab_<tweetid>/v<outer>/...`) is set.
2. `sqlite-leads`: `UPDATE leads SET dev_status='done', updated_at=datetime('now') WHERE tweet_id='<ID>';`
3. Record the handoff to sales in kanban (`handoff` → sales role).

## OUTPUT
- The lead in `dev_status='done'` with `dev_artifact` filled in, marked as ready for sale.

## NEXT
- Sales (cron `sl-*`) will pick up the lead. orchestrator_global → `og-close-day`.

## LIMITS
- Do not hand off to sales without a confirmed artifact in MinIO. I do not run the dialog/Stripe myself — that is sales.
