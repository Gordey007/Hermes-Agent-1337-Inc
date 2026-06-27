"""IMMUTABLE evaluator (Karpathy's three-file contract).

The developer agent does NOT edit this file. It reads the DoD from design/dod.md (or dod.json),
brings the product up in isolation, and runs the checks. The result is a numeric score [0..1] +
textual feedback (this is also the metric format for DSPy in dspy_eval.py).

A DoD check = a list of checks. Each check: {id, kind, ...}. Supported kinds:
  - file_exists:   {"path": "..."}                          file exists in product/
  - cmd:           {"run": "...", "expect_code": 0}         command in the product directory
  - http:          {"url": "...", "expect_status": 200}     HTTP check of the running service
  - contains:      {"path": "...", "substr": "..."}         substring in a file

score = fraction of passed checks (weighted by weight, default 1).
"""
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import httpx

from dotenv import load_dotenv
load_dotenv()

def _check_file_exists(product: Path, c: dict) -> tuple[bool, str]:
    ok = (product / c["path"]).exists()
    return ok, "" if ok else f"missing file {c['path']}"


def _check_contains(product: Path, c: dict) -> tuple[bool, str]:
    p = product / c["path"]
    if not p.exists():
        return False, f"missing file {c['path']}"
    ok = c["substr"] in p.read_text(encoding="utf-8", errors="replace")
    return ok, "" if ok else f"{c['path']} lacks '{c['substr']}'"


def _check_cmd(product: Path, c: dict) -> tuple[bool, str]:
    try:
        r = subprocess.run(c["run"], shell=True, cwd=product, capture_output=True,
                           text=True, timeout=c.get("timeout", 120))
    except subprocess.TimeoutExpired:
        return False, f"timeout: {c['run']}"
    ok = r.returncode == c.get("expect_code", 0)
    return ok, "" if ok else f"cmd `{c['run']}` rc={r.returncode}: {r.stderr[-300:]}"


def _check_http(product: Path, c: dict) -> tuple[bool, str]:
    try:
        r = httpx.get(c["url"], timeout=c.get("timeout", 15))
    except Exception as e:  # noqa: BLE001 — any network failure = check failure
        return False, f"http error {c['url']}: {e}"
    ok = r.status_code == c.get("expect_status", 200)
    return ok, "" if ok else f"{c['url']} status={r.status_code}"


_CHECKS = {
    "file_exists": _check_file_exists,
    "contains": _check_contains,
    "cmd": _check_cmd,
    "http": _check_http,
}


def load_dod(path: str) -> list[dict]:
    """DoD from a JSON file (or dod.json next to dod.md)."""
    p = Path(path)
    if p.suffix == ".md":
        cand = p.with_suffix(".json")
        if cand.exists():
            p = cand
    return json.loads(p.read_text(encoding="utf-8")).get("checks", [])


def evaluate(product_dir: str, dod_path: str) -> dict:
    product = Path(product_dir)
    checks = load_dod(dod_path)
    if not checks:
        return {"score": 0.0, "passed": 0, "total": 0,
                "feedback": "DoD is empty — nothing to check", "results": []}

    results, gained, total_w = [], 0.0, 0.0
    for c in checks:
        w = float(c.get("weight", 1))
        total_w += w
        fn = _CHECKS.get(c["kind"])
        if fn is None:
            results.append({"id": c.get("id"), "ok": False, "msg": f"unknown kind {c['kind']}"})
            continue
        ok, msg = fn(product, c)
        if ok:
            gained += w
        results.append({"id": c.get("id"), "kind": c["kind"], "ok": ok, "msg": msg})

    score = gained / total_w if total_w else 0.0
    fails = [r for r in results if not r["ok"]]
    feedback = ("All checks passed." if not fails
                else "Failures: " + "; ".join(f"{r['id']}: {r['msg']}" for r in fails))
    return {"score": round(score, 4), "passed": len(results) - len(fails),
            "total": len(results), "feedback": feedback, "results": results}


if __name__ == "__main__":
    import argparse
    ap = argparse.ArgumentParser(description="DoD evaluator (immutable)")
    ap.add_argument("--product", required=True)
    ap.add_argument("--dod", required=True)
    args = ap.parse_args()
    out = evaluate(args.product, args.dod)
    print(json.dumps(out, ensure_ascii=False, indent=2))
    sys.exit(0 if out["score"] >= 1.0 else 1)
