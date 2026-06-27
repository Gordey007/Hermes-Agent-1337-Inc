"""Iteration counter sidecar for the built-in Hermes kanban.

The kanban itself (a Hermes tool, DB at ~/.hermes/kanban.db) stores tasks/statuses/comments,
but does NOT track our iteration limits. This file holds only counters, keyed by (tweet_id, sprint, counter).

Default limits:
  dev_architect=5, architect_researcher=5, github_search=10, inner_loop=10, outer_loop=10

CLI:
  python counters.py inc  --tweet <id> --sprint N --counter <name> [--by 1]
  python counters.py get  --tweet <id> --sprint N --counter <name>
  python counters.py list --tweet <id> --sprint N
  python counters.py reset --tweet <id> --sprint N [--counter <name>]
"""
from __future__ import annotations

import argparse
import json
import os
import sqlite3
import sys
from pathlib import Path

DB_PATH = Path(os.getenv("COUNTERS_DB_PATH", "/sandbox/kanban/counters.db"))

LIMITS = {
    "dev_architect": 5,
    "architect_researcher": 5,
    "github_search": 10,
    "inner_loop": 10,
    "outer_loop": 10,
}

SCHEMA = """
CREATE TABLE IF NOT EXISTS counters (
    tweet_id TEXT NOT NULL,
    sprint   INTEGER NOT NULL,
    counter  TEXT NOT NULL,
    value    INTEGER NOT NULL DEFAULT 0,
    PRIMARY KEY (tweet_id, sprint, counter)
)
"""


def get_conn() -> sqlite3.Connection:
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute(SCHEMA)
    return conn


def _limit(counter: str) -> int:
    return LIMITS.get(counter, 10)


def inc(tweet: str, sprint: int, counter: str, by: int = 1) -> dict:
    with get_conn() as conn:
        conn.execute(
            "INSERT INTO counters (tweet_id, sprint, counter, value) VALUES (?,?,?,?) "
            "ON CONFLICT(tweet_id, sprint, counter) DO UPDATE SET value = value + ?",
            (str(tweet), sprint, counter, by, by))
        conn.commit()
        row = conn.execute(
            "SELECT value FROM counters WHERE tweet_id=? AND sprint=? AND counter=?",
            (str(tweet), sprint, counter)).fetchone()
    value = row["value"]
    limit = _limit(counter)
    return {"counter": counter, "value": value, "max": limit, "over_limit": value > limit}


def get(tweet: str, sprint: int, counter: str) -> dict:
    with get_conn() as conn:
        row = conn.execute(
            "SELECT value FROM counters WHERE tweet_id=? AND sprint=? AND counter=?",
            (str(tweet), sprint, counter)).fetchone()
    value = row["value"] if row else 0
    limit = _limit(counter)
    return {"counter": counter, "value": value, "max": limit, "over_limit": value > limit}


def list_all(tweet: str, sprint: int) -> list:
    with get_conn() as conn:
        rows = conn.execute(
            "SELECT counter, value FROM counters WHERE tweet_id=? AND sprint=? ORDER BY counter",
            (str(tweet), sprint)).fetchall()
    return [{"counter": r["counter"], "value": r["value"],
             "max": _limit(r["counter"]), "over_limit": r["value"] > _limit(r["counter"])}
            for r in rows]


def reset(tweet: str, sprint: int, counter: str | None) -> dict:
    with get_conn() as conn:
        if counter:
            conn.execute("DELETE FROM counters WHERE tweet_id=? AND sprint=? AND counter=?",
                         (str(tweet), sprint, counter))
        else:
            conn.execute("DELETE FROM counters WHERE tweet_id=? AND sprint=?",
                         (str(tweet), sprint))
        conn.commit()
    return {"reset": counter or "*", "tweet": str(tweet), "sprint": sprint}


def main() -> None:
    p = argparse.ArgumentParser(description="Hermes-kanban iteration counters (sidecar)")
    sub = p.add_subparsers(dest="cmd", required=True)
    for name in ("inc", "get"):
        sp = sub.add_parser(name)
        sp.add_argument("--tweet", required=True)
        sp.add_argument("--sprint", type=int, required=True)
        sp.add_argument("--counter", required=True)
        if name == "inc":
            sp.add_argument("--by", type=int, default=1)
    lp = sub.add_parser("list")
    lp.add_argument("--tweet", required=True)
    lp.add_argument("--sprint", type=int, required=True)
    rp = sub.add_parser("reset")
    rp.add_argument("--tweet", required=True)
    rp.add_argument("--sprint", type=int, required=True)
    rp.add_argument("--counter")

    args = p.parse_args()
    if args.cmd == "inc":
        out = inc(args.tweet, args.sprint, args.counter, args.by)
    elif args.cmd == "get":
        out = get(args.tweet, args.sprint, args.counter)
    elif args.cmd == "list":
        out = list_all(args.tweet, args.sprint)
    elif args.cmd == "reset":
        out = reset(args.tweet, args.sprint, args.counter)
    else:  # pragma: no cover
        sys.exit(2)
    print(json.dumps(out, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
