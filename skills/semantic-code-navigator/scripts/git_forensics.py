#!/usr/bin/env python3
"""Git Evolutionary Forensics — Hidden Co-Change Twins & Bug-Magnet Miner (`git_forensics.py` — v12.0 Quantum).

Mines Git commit history (`git log`) to uncover invisible architectural traps that
static AST import graphs can NEVER see:
1. "Invisible Co-Change Twins": Pairs of files (e.g. `backend/webhook.py` & `mobile/plan.dart`)
   that co-change together in >=60% of commits — modifying one without checking its twin causes silent bugs!
2. "Bug-Magnet Hotzones": Files most frequently touched in `fix` / `bug` / `hotfix` / `revert` commits.
"""

from __future__ import annotations

import argparse
import collections
import json
import re
import subprocess
from pathlib import Path
from typing import Any, Dict, List, Tuple

BUG_COMMIT_RE = re.compile(r"\b(?:fix|bug|hotfix|revert|crash|patch|broken|issue)\b", re.IGNORECASE)


def parse_git_log_commits(raw_log: str) -> List[Dict[str, Any]]:
    commits: List[Dict[str, Any]] = []
    current: Dict[str, Any] | None = None

    for raw_ln in raw_log.splitlines():
        ln = raw_ln.strip()
        if not ln:
            continue
        if ln.startswith("__COMMIT__|"):
            parts = ln.split("|", 2)
            current = {
                "sha": parts[1] if len(parts) > 1 else "",
                "subject": parts[2] if len(parts) > 2 else "",
                "files": [],
            }
            commits.append(current)
        elif current is not None and not ln.startswith("commit "):
            norm = ln.replace("\\", "/")
            if len(current["files"]) < 25 and norm not in current["files"]:
                current["files"].append(norm)
    return commits


def analyze_commits_forensics(commits: List[Dict[str, Any]], min_shared: int = 2) -> Dict[str, Any]:
    file_touches: Dict[str, int] = collections.Counter()
    bug_touches: Dict[str, int] = collections.Counter()
    pair_counts: Dict[Tuple[str, str], int] = collections.Counter()

    for c in commits:
        files = sorted(set(c.get("files") or []))
        if not files or len(files) > 20:
            # Skip mega-initial commits (>20 files) so co-change signal stays razor-sharp
            for f in files:
                file_touches[f] += 1
            continue

        is_bug = bool(BUG_COMMIT_RE.search(str(c.get("subject") or "")))
        for f in files:
            file_touches[f] += 1
            if is_bug:
                bug_touches[f] += 1

        for i in range(len(files)):
            for j in range(i + 1, len(files)):
                pair_counts[(files[i], files[j])] += 1

    invisible_twins: List[Dict[str, Any]] = []
    for (fa, fb), shared in pair_counts.most_common(40):
        if shared < min_shared:
            continue
        denom = min(file_touches[fa], file_touches[fb])
        confidence = round((shared / max(1, denom)) * 100, 1)
        if confidence >= 55.0:
            invisible_twins.append(
                {
                    "file_a": fa,
                    "file_b": fb,
                    "shared_commits": shared,
                    "coupling_pct": confidence,
                }
            )

    bug_magnets = [
        {"file": f, "bugfix_commits": cnt, "total_commits": file_touches[f]}
        for f, cnt in bug_touches.most_common(10)
    ]

    return {
        "analyzed_commits": len(commits),
        "invisible_twins": invisible_twins[:12],
        "bug_magnets": bug_magnets,
    }


def run_git_forensics(workspace: Path, max_commits: int = 120) -> Dict[str, Any]:
    workspace = workspace.resolve()
    try:
        proc = subprocess.run(
            ["git", "log", f"-n{max_commits}", "--name-only", "--pretty=format:__COMMIT__|%h|%s"],
            cwd=str(workspace),
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=10,
        )
        raw = proc.stdout if proc.returncode == 0 else ""
    except Exception:
        raw = ""

    commits = parse_git_log_commits(raw)
    return analyze_commits_forensics(commits)


def render_markdown(rep: Dict[str, Any]) -> str:
    lines = [f"### 🕵️‍♂️ Git Evolutionary Forensics (`{rep['analyzed_commits']}` commits mined)"]
    if rep["invisible_twins"]:
        lines.append("\n#### 🔗 Hidden Co-Change Twins (Update Both Together!)")
        for t in rep["invisible_twins"]:
            lines.append(f"- `{t['file_a']}` ↔ `{t['file_b']}` — **{t['coupling_pct']}% coupled** ({t['shared_commits']} shared commits)")
    else:
        lines.append("- _No tight multi-commit co-change twins detected yet._")

    if rep["bug_magnets"]:
        lines.append("\n#### 🧲 Historical Bug-Magnet Hotzones")
        for b in rep["bug_magnets"]:
            lines.append(f"- `{b['file']}` — **{b['bugfix_commits']} bugfix commits** (out of {b['total_commits']} touches)")
    return "\n".join(lines)


def main() -> int:
    ap = argparse.ArgumentParser(description="Git Co-Change Twins & Bug-Magnet Miner")
    ap.add_argument("--workspace", default=".")
    ap.add_argument("--max-commits", type=int, default=120)
    ap.add_argument("--json", action="store_true")
    ns = ap.parse_args()
    rep = run_git_forensics(Path(ns.workspace), max_commits=ns.max_commits)
    print(json.dumps(rep, indent=2, ensure_ascii=False) if ns.json else render_markdown(rep))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
