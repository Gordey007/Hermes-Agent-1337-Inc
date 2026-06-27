#!/usr/bin/env python3
"""dod_eval.py — immutable DoD evaluator for notes_api.

Hits the running service (TARGET_URL), runs the checks from dod.json,
prints a JSON verdict to stdout and exits with code 0 if pass_rate >= threshold.

Run (inside the eval container):
    TARGET_URL=http://app:8000 python dod_eval.py
"""
import json
import os
import sys
import time
import urllib.error
import urllib.request

BASE = os.environ.get("TARGET_URL", "http://localhost:8000").rstrip("/")
HERE = os.path.dirname(os.path.abspath(__file__))

with open(os.path.join(HERE, "dod.json"), encoding="utf-8") as f:
    DOD = json.load(f)


def req(method, path, body=None, expect=None):
    url = BASE + path
    data = json.dumps(body).encode() if body is not None else None
    r = urllib.request.Request(url, data=data, method=method)
    if data is not None:
        r.add_header("Content-Type", "application/json")
    try:
        with urllib.request.urlopen(r, timeout=5) as resp:
            code = resp.status
            raw = resp.read()
    except urllib.error.HTTPError as e:
        code = e.code
        raw = e.read()
    payload = None
    if raw:
        try:
            payload = json.loads(raw)
        except ValueError:
            payload = None
    if expect is not None and code != expect:
        raise AssertionError(f"{method} {path}: expected {expect}, got {code}")
    return code, payload


def wait_ready(retries=30, delay=1.0):
    for _ in range(retries):
        try:
            code, _ = req("GET", "/health")
            if code == 200:
                return True
        except OSError:
            pass
        time.sleep(delay)
    return False


def run_checks():
    results = {}

    # health
    try:
        code, body = req("GET", "/health", expect=200)
        results["health"] = body == {"status": "ok"}
    except AssertionError:
        results["health"] = False

    # create
    nid = None
    try:
        code, body = req("POST", "/notes", {"title": "t1", "body": "b1"}, expect=201)
        nid = body.get("id")
        results["create"] = isinstance(nid, int)
    except AssertionError:
        results["create"] = False

    # get
    try:
        if nid is None:
            raise AssertionError("no id")
        code, body = req("GET", f"/notes/{nid}", expect=200)
        results["get"] = body.get("title") == "t1" and body.get("body") == "b1"
    except AssertionError:
        results["get"] = False

    # list
    try:
        code, body = req("GET", "/notes", expect=200)
        results["list"] = any(n.get("id") == nid for n in (body or []))
    except AssertionError:
        results["list"] = False

    # delete
    try:
        if nid is None:
            raise AssertionError("no id")
        req("DELETE", f"/notes/{nid}", expect=204)
        code, _ = req("GET", f"/notes/{nid}")
        results["delete"] = code == 404
    except AssertionError:
        results["delete"] = False

    # not_found
    try:
        code, _ = req("GET", "/notes/999999")
        results["not_found"] = code == 404
    except AssertionError:
        results["not_found"] = False

    return results


def main():
    if not wait_ready():
        print(json.dumps({"error": "service didn't come up", "target": BASE}))
        sys.exit(2)

    results = run_checks()
    total = len(results)
    passed = sum(1 for v in results.values() if v)
    pass_rate = round(passed / total, 4) if total else 0.0
    threshold = DOD.get("threshold", 1.0)
    verdict = "keep" if pass_rate >= threshold else "rollback"

    report = {
        "component": DOD["component"],
        "metric": "pass_rate",
        "pass_rate": pass_rate,
        "passed": passed,
        "total": total,
        "threshold": threshold,
        "verdict": verdict,
        "checks": results,
        "target": BASE,
    }
    print(json.dumps(report, ensure_ascii=False, indent=2))
    sys.exit(0 if pass_rate >= threshold else 1)


if __name__ == "__main__":
    main()
