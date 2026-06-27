---
name: sqlite-leads
description: Read and write lead statuses in leads.db (qualification, dev_status, offer/reply).
version: 1.0.0
author: hermes-team
license: MIT
metadata:
  hermes:
    requires_toolsets: [sqlite]
---

# sqlite-leads

## WHO
Any profile that needs to read/update a lead: orchestrator_global, sales.

## WHEN
- Before selecting a task (qualification), when changing `dev_status`, when sending an offer / analyzing a reply.
- Trigger: a kanban status requires syncing with the `leads` table.

## STEPS
DB: `$LEADS_DB_PATH` (defaults to `/sandbox/x_lead/leads.db`). The `sqlite3` wrapper is
`/sandbox/.local/bin/sqlite3`.

1. Read candidates:
   `sqlite3 $LEADS_DB_PATH "SELECT tweet_id, author_username, tweet_text FROM leads WHERE is_relevant=1 AND dev_status='pending' ORDER BY impression_count DESC LIMIT 20;"`
2. Qualification: `UPDATE leads SET is_relevant=1, updated_at=datetime('now') WHERE tweet_id='<ID>';`
3. Take into work: `UPDATE leads SET dev_status='in_progress', updated_at=datetime('now') WHERE tweet_id='<ID>';`
4. Done: `UPDATE leads SET dev_status='done', dev_artifact='<minio-key>', updated_at=datetime('now') WHERE tweet_id='<ID>';`
5. Failure: `UPDATE leads SET dev_status='failed', updated_at=datetime('now') WHERE tweet_id='<ID>';`
6. Offer/reply: `offer_sent=1, reply_status='no_reply'` → then `reply_status` ∈ positive/negative/done + `reply_summary`.
   Escape quotes inside summary with `sed "s/'/''/g"`.

## OUTPUT
- Updated fields of the `leads` row (`is_relevant`/`dev_status`/`dev_artifact`/`offer_sent`/`reply_*`).
- Always set `updated_at=datetime('now')` (needed for the sales cooldown).

## NEXT
- After `dev_status='done'` → orchestrator_global calls `og-handoff-sales`.
- After `reply_status='done'` (paid) → sales calls `sl-deliver`.

## LIMITS
- One lead per cron run (anti-ban). Do not touch other roles' fields outside your own role (see AGENT.md OWNS).
