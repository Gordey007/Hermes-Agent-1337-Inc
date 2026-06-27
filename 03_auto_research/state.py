"""Sprint persistence: progress.jsonl (step log) + session.md (human-readable).

Karpathy's three-file contract requires durability across steps/iterations: every
keep/rollback is recorded and the DoD metric is saved in order to decide keep-or-rollback.
"""
from __future__ import annotations

import json
import time
from pathlib import Path


class SprintState:
    def __init__(self, sprint_dir: str):
        self.dir = Path(sprint_dir)
        self.dir.mkdir(parents=True, exist_ok=True)
        self.progress = self.dir / "reports" / "progress.jsonl"
        self.session = self.dir / "reports" / "session.md"
        self.progress.parent.mkdir(parents=True, exist_ok=True)
        self.best_score = self._load_best()

    def _load_best(self) -> float:
        best = 0.0
        if self.progress.exists():
            for line in self.progress.read_text(encoding="utf-8").splitlines():
                try:
                    rec = json.loads(line)
                    best = max(best, rec.get("score", 0.0))
                except json.JSONDecodeError:
                    continue
        return best

    def log(self, loop: str, iteration: int, action: str, score: float,
            kept: bool, feedback: str = "", component: str | None = None) -> None:
        rec = {
            "ts": time.strftime("%Y-%m-%dT%H:%M:%S"),
            "loop": loop, "iteration": iteration, "component": component,
            "action": action, "score": round(score, 4),
            "best": round(self.best_score, 4), "kept": kept, "feedback": feedback[:500],
        }
        with self.progress.open("a", encoding="utf-8") as f:
            f.write(json.dumps(rec, ensure_ascii=False) + "\n")
        self._append_session(rec)

    def _append_session(self, rec: dict) -> None:
        line = (f"- `{rec['ts']}` **{rec['loop']}#{rec['iteration']}** "
                f"{rec.get('component') or ''} {rec['action']} → "
                f"score={rec['score']} (best={rec['best']}) "
                f"{'KEEP' if rec['kept'] else 'ROLLBACK'}\n")
        if not self.session.exists():
            self.session.write_text("# Session log\n\n", encoding="utf-8")
        with self.session.open("a", encoding="utf-8") as f:
            f.write(line)

    def keep_if_better(self, score: float) -> bool:
        """Return True (keep) if the metric improved, otherwise False (rollback)."""
        if score > self.best_score:
            self.best_score = score
            return True
        return False
