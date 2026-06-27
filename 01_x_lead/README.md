# 01_x_lead — X/Twitter lead hunting

This subproject searches X/Twitter for fresh tweets that signal a willingness to pay,
hire, or look for a tool, filters out bots, and writes leads into the SQLite `leads`
table. It is the entry point of the whole pipeline.

## Layout

| File | Purpose |
|---|---|
| `db.py` | **Single source** of the schema and DB connection (`get_conn`, `init_db`). Path comes from `LEADS_DB_PATH`. |
| `create_db.py` | Recreate the `leads` table. `python create_db.py` (DROP+CREATE) or `--keep` (CREATE IF NOT EXISTS). |
| `queries.yaml` | Search intents (X API v2 syntax). Editable without touching code. |
| `x_lead_hunter.py` | Recent search + bot filter + write (`run_once`). |

## Environment variables

```bash
export X_BEARER_TOKEN="<X API v2 bearer token>"   # provide via your own secret store
export LEADS_DB_PATH="/sandbox/x_lead/leads.db"   # single DB path (must match everywhere)
```

`LEADS_DB_PATH` must be identical for `create_db.py` and `x_lead_hunter.py` — otherwise you
get the `table leads has no column named tweet_id` bug (path mismatch). That is why the path
is defined by a **single** environment variable and every connection goes **only** through
`db.get_conn()`.

## First run

```bash
rm -f "$LEADS_DB_PATH" "$LEADS_DB_PATH"-wal "$LEADS_DB_PATH"-shm   # drop the old DB and WAL/SHM
python 01_x_lead/create_db.py                                      # create table + indexes
python 01_x_lead/x_lead_hunter.py                                  # one pass over all intents
```

Schema check: `sqlite3 "$LEADS_DB_PATH" "PRAGMA table_info(leads)"` must include `tweet_id`.

## Cron (autonomous mode)

```cron
*/30 * * * * cd /sandbox && LEADS_DB_PATH=/sandbox/x_lead/leads.db python 01_x_lead/x_lead_hunter.py >> /sandbox/logs/x_lead.log 2>&1
```

The search window is the last 24 hours, `sort_order=relevancy`. `INSERT OR IGNORE` on
`tweet_id` keeps the run idempotent: repeated runs do not create duplicates.

## OpenShell policy

The profile/cron only needs network access to `api.x.com`. Example policy:

```yaml
network:
  allow:
    - api.x.com
```

## Intents (`queries.yaml`)

- `willing_to_pay` — explicit willingness to pay (the hottest lead);
- `hiring` — looking to hire someone;
- `looking_for_tool` — an explicit lack of a tool;
- `pain_point` — pain from a manual, repetitive chore.

Each intent has `intent`, `query` (X API v2 operators), and `rationale`. Adding a new intent
is just a new list item — no code changes needed.

## What's next

The written leads (`dev_status='pending'`, `is_relevant=0`) are picked up by
**orchestrator_global** (subproject `02_sales_pipeline`): it qualifies them (`is_relevant=1`)
and starts a sprint.
