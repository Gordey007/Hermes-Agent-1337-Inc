"""Cache of GitHub responses by request key/ETag — to avoid burning rate-limit on repeats.

A simple file-based JSON cache. Stores per key: etag, status, payload, timestamp.
GitHub returns an `ETag`; on a repeat we send `If-None-Match` and take the cache on a 304.
"""
from __future__ import annotations

import hashlib
import json
import os
import time
from pathlib import Path

CACHE_DIR = Path(os.getenv("GH_CACHE_DIR", ".gh_cache"))
TTL_SECONDS = int(os.getenv("GH_CACHE_TTL", str(6 * 3600)))


def _key(raw: str) -> str:
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()[:32]


def _path(raw: str) -> Path:
    return CACHE_DIR / f"{_key(raw)}.json"


def get(raw: str) -> dict | None:
    p = _path(raw)
    if not p.exists():
        return None
    try:
        data = json.loads(p.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return None
    if time.time() - data.get("ts", 0) > TTL_SECONDS:
        return data  # expired by TTL, but the etag is still good for If-None-Match
    return data


def put(raw: str, etag: str | None, status: int, payload) -> None:
    CACHE_DIR.mkdir(parents=True, exist_ok=True)
    _path(raw).write_text(
        json.dumps({"etag": etag, "status": status, "payload": payload, "ts": time.time()},
                   ensure_ascii=False),
        encoding="utf-8",
    )


def fresh(raw: str) -> dict | None:
    """Return the cache only if it is not expired by TTL (can be served without a network request)."""
    data = get(raw)
    if data and time.time() - data.get("ts", 0) <= TTL_SECONDS:
        return data
    return None
