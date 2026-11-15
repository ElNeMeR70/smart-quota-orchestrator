#!/usr/bin/env python3
"""N+1 Query, Async Waterfall & Flutter UI-Jank Performance Profiler (`perf_profiler.py` — v11.0 Hypernova).

Catches silent production performance killers introduced by AI coding agents:
1. Database / HTTP N+1 Queries inside loops (`for`/`while`/`.map` containing DB/fetch calls)
2. Sequential `await` waterfalls (consecutive independent awaits instead of `Promise.all`/`gather`)
3. Flutter UI Jank & Memory Leaks (`TextEditingController` without `dispose()`, heavy sync JSON decode in `build()`)
4. Unbounded `SELECT *` without `LIMIT` on large tables
"""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from typing import Any, Dict, List

LOOP_START_RE = re.compile(r"^\s*(?:for\s*\(|for\s+\w+\s+in\b|async\s+for\b|while\s*\(|foreach\s*\()")
DB_OR_IO_CALL_RE = re.compile(
    r"(?:\bawait\s+(?:prisma|db|supabase|axios|fetch|http|dio|client)\b|\.(?:findUnique|findFirst|findMany|execute|query)\s*\(|::(?:where|find)\s*\()"
)
AWAIT_ASSIGN_RE = re.compile(r"^\s*(?:const|let|var|final)?\s*(\w+)\s*=\s*await\s+([^;]+)")
UNBOUNDED_SQL_RE = re.compile(r"\bSELECT\s+\*\s+FROM\s+\w+\s*(?:;|$|\"|')", re.IGNORECASE)

SKIP_DIRS = {".git", "node_modules", ".venv", "venv", "__pycache__", "build", "dist", ".next", ".dart_tool", "vendor", ".sqo", "tests"}


def analyze_file_performance(text: str, ext: str, rel_file: str = "snippet") -> List[Dict[str, Any]]:
    issues: List[Dict[str, Any]] = []
    lines = text.splitlines()

    # 1. Detect N+1 DB/Network queries inside loop windows (next 8 lines)
    for idx, ln in enumerate(lines):
        if LOOP_START_RE.search(ln):
            loop_indent = len(ln) - len(ln.lstrip(" "))
            for j in range(idx + 1, min(len(lines), idx + 10)):
                body_ln = lines[j]
                if not body_ln.strip():
                    continue
                cur_indent = len(body_ln) - len(body_ln.lstrip(" "))
                if ext == ".py" and cur_indent <= loop_indent:
                    break
                if DB_OR_IO_CALL_RE.search(body_ln):
                    issues.append(
                        {
                            "kind": "n_plus_1_query_in_loop",
                            "severity": "high",
                            "file": rel_file,
                            "line": j + 1,
                            "detail": f"DB/Network query inside loop (`{body_ln.strip()[:75]}`). Batch with `WHERE IN` / `include` / `Promise.all`.",
                        }
                    )
                    break

    # 2. Detect Sequential Async Waterfall (2 consecutive awaits where 2nd doesn't reference 1st variable)
    for idx in range(len(lines) - 1):
        m1 = AWAIT_ASSIGN_RE.search(lines[idx])
        m2 = AWAIT_ASSIGN_RE.search(lines[idx + 1])
        if m1 and m2:
            var1 = m1.group(1)
            rhs2 = m2.group(2)
            if not re.search(rf"\b{re.escape(var1)}\b", rhs2):
                issues.append(
                    {
                        "kind": "sequential_async_waterfall",
                        "severity": "medium",
                        "file": rel_file,
                        "line": idx + 1,
                        "detail": f"Independent sequential `await` calls (`{var1}`, `{m2.group(1)}`). Parallelize via `Promise.all` / `Future.wait` / `asyncio.gather`.",
                    }
                )

    # 3. Flutter Controller Memory Leak & UI-Thread Jank
    if ext == ".dart":
        if "TextEditingController(" in text and ".dispose(" not in text:
            issues.append(
                {
                    "kind": "flutter_controller_leak",
                    "severity": "high",
                    "file": rel_file,
                    "line": 1,
                    "detail": "`TextEditingController` instantiated without calling `.dispose()` in `State.dispose()`.",
                }
            )
        if re.search(r"Widget\s+build\s*\([^)]*\)\s*\{[\s\S]{0,600}?jsonDecode\s*\(", text):
            issues.append(
                {
                    "kind": "flutter_build_jank",
                    "severity": "medium",
                    "file": rel_file,
                    "line": 1,
                    "detail": "`jsonDecode()` executed directly inside `Widget build()` (runs at 60/120Hz!). Move to state/provider.",
                }
            )

    # 4. Unbounded SELECT * without WHERE/LIMIT
    for idx, ln in enumerate(lines, 1):
        if UNBOUNDED_SQL_RE.search(ln) and "LIMIT" not in ln.upper():
            issues.append(
                {
                    "kind": "unbounded_select_star",
                    "severity": "low",
                    "file": rel_file,
                    "line": idx,
                    "detail": "Unbounded `SELECT *` without explicit column projection or `LIMIT` pagination.",
                }
            )

    return issues


def profile_workspace_performance(workspace: Path) -> Dict[str, Any]:
    workspace = workspace.resolve()
    exts = {".py", ".ts", ".tsx", ".js", ".jsx", ".dart", ".php", ".go"}
    findings: List[Dict[str, Any]] = []
    scanned = 0

    for p in workspace.rglob("*"):
        if not p.is_file() or p.suffix.lower() not in exts:
            continue
        if any(part in SKIP_DIRS for part in p.parts) or p.name == "perf_profiler.py":
            continue
        scanned += 1
        try:
            txt = p.read_text(encoding="utf-8", errors="ignore")
        except OSError:
            continue
        rel = str(p.relative_to(workspace)).replace("\\", "/")
        findings.extend(analyze_file_performance(txt, p.suffix.lower(), rel))
        if len(findings) >= 35:
            break

    high = sum(1 for f in findings if f["severity"] == "high")
    med = sum(1 for f in findings if f["severity"] == "medium")
    score = max(0, 100 - high * 20 - med * 10 - (len(findings) - high - med) * 4)

    return {
        "perf_score": score,
        "scanned_files": scanned,
        "issue_count": len(findings),
        "n_plus_1_count": sum(1 for f in findings if f["kind"] == "n_plus_1_query_in_loop"),
        "issues": findings[:35],
    }


def render_markdown(rep: Dict[str, Any]) -> str:
    lines = [
        f"### ⚡ Static N+1, Async Waterfall & UI-Jank Profiler (`{rep['perf_score']}/100`)",
        f"- **Scanned Files:** `{rep['scanned_files']}` | **Hotspots:** `{rep['issue_count']}` (`{rep['n_plus_1_count']}` N+1 query loops)",
    ]
    for i in rep["issues"][:15]:
        lines.append(f"- **[{i['severity'].upper()} • `{i['kind']}`]** `{i['file']}:L{i['line']}` — {i['detail']}")
    if not rep["issues"]:
        lines.append("- ✅ **Zero N+1 query loops, async waterfalls, or Flutter UI memory leaks detected!**")
    return "\n".join(lines)


def main() -> int:
    ap = argparse.ArgumentParser(description="N+1 Query & Async Performance Profiler")
    ap.add_argument("--workspace", default=".")
    ap.add_argument("--json", action="store_true")
    ns = ap.parse_args()
    rep = profile_workspace_performance(Path(ns.workspace))
    print(json.dumps(rep, indent=2, ensure_ascii=False) if ns.json else render_markdown(rep))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
