"""A single source for the schema and database connection for leads.

The root cause of the bug `table leads has no column named tweet_id` was a path desynchronization:
`create_db.py` used the absolute path `/sandbox/x_lead/leads.db`, while
`x_lead_hunter.get_conn()` used the relative path `Path(__file__).parent / "leads.db"`.
Now, the single source of truth is this module.

The path to the database is controlled by the LEADS_DB_PATH environment variable (by default, the
sandbox working directory). Both create_db.py and x_lead_hunter.py import
get_conn() from here.
"""

import os
import sqlite3
from pathlib import Path

from dotenv import load_dotenv
load_dotenv()


DB_PATH = Path(os.getenv("LEADS_DB_PATH", "/sandbox/tools/x_lead/leads.db"))


def get_conn() -> sqlite3.Connection:
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA foreign_keys=ON")
    return conn


SCHEMA = """
CREATE TABLE IF NOT EXISTS leads (
    tweet_id            TEXT PRIMARY KEY,
    tweet_url           TEXT NOT NULL,
    tweet_text          TEXT NOT NULL,
    author_id           TEXT NOT NULL,
    author_username     TEXT NOT NULL,
    lang                TEXT,
    created_at          TEXT,
    impression_count    INTEGER DEFAULT 0,
    like_count          INTEGER DEFAULT 0,
    reply_count         INTEGER DEFAULT 0,
    retweet_count       INTEGER DEFAULT 0,
    is_relevant         INTEGER NOT NULL DEFAULT 0,
    project_concept     TEXT,
    project_complexity  INTEGER,
    dev_status          TEXT NOT NULL DEFAULT 'pending'
                        CHECK(dev_status IN ('pending','in_progress','done','failed')),
    offer_sent          INTEGER NOT NULL DEFAULT 0,
    reply_status        TEXT DEFAULT NULL
                        CHECK(reply_status IN (NULL,'done','positive','negative','no_reply')),
    reply_summary       TEXT DEFAULT NULL,
    dev_artifact        TEXT DEFAULT NULL,
    inserted_at         TEXT NOT NULL DEFAULT (datetime('now')),
    updated_at          TEXT NOT NULL DEFAULT (datetime('now'))
)
"""

INDEXES = [
    "CREATE INDEX IF NOT EXISTS idx_is_relevant  ON leads(is_relevant)",
    "CREATE INDEX IF NOT EXISTS idx_dev_status   ON leads(dev_status)",
    "CREATE INDEX IF NOT EXISTS idx_offer_sent   ON leads(offer_sent)",
    "CREATE INDEX IF NOT EXISTS idx_reply_status ON leads(reply_status)",
    "CREATE INDEX IF NOT EXISTS idx_author_id    ON leads(author_id)",
]


def init_db(drop: bool = False) -> None:
    with get_conn() as conn:
        if drop:
            conn.execute("DROP TABLE IF EXISTS leads")
        conn.execute(SCHEMA)
        for idx in INDEXES:
            conn.execute(idx)
        conn.commit()
    print(f"[init_db] OK Database ready: {DB_PATH}")
