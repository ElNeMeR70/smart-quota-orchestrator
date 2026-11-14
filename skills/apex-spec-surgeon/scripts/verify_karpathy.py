#!/usr/bin/env python3
"""Karpathy + Superpowers Executable Diff & Anti-Laziness Gatekeeper (v10.0 Apex).

Turns Andrej Karpathy's 210k-star guidelines into a deterministic code gatekeeper:
1. Laziness / Truncation Detector (`TODO`, `rest of code`, `UnimplementedError`, `NotImplementedError`)
2. Silent Feature Deletion Detector (functions/classes/routes removed without replacement)
3. Surgical Scope Creep Detector (files touched outside allowed_files)
4. Over-Engineering / Complexity Spike Detector
"""

from __future__ import annotations

import argparse
import json
import re
import subprocess
from pathlib import Path
from typing import Any, Dict, List, Optional, Set

LAZINESS_PATTERNS = [
    (re.compile(r"(?://|#|--|/\*)\s*(?:TODO|FIXME|XXX)\b", re.IGNORECASE), "Unfinished TODO/FIXME comment"),
    (re.compile(r"(?://|#)\s*\.\.\.\s*(?:rest of|existing|remaining|unchanged|keep)\b", re.IGNORECASE), "Truncated code placeholder comment"),
    (re.compile(r"\b(?:throw\s+const\s+UnimplementedError|throw\s+UnimplementedError|raise\s+NotImplementedError)\b"), "Unimplemented stub exception"),
    (re.compile(r"^\s*\.\.\.\s*#\s*stub\b", re.IGNORECASE), "Python ellipsis stub"),
]

SYMBOL_DEF_RE = re.compile(
    r"^\s*(?:export\s+)?(?:default\s+)?(?:async\s+)?(?:def|class|function|func|fn|pub\s+fn|interface)\s+([A-Za-z_]\w*)\b"
)


def _get_git_diff(workspace: Path) -> str:
    try:
        proc = subprocess.run(
            ["git", "diff", "HEAD"],
            cwd=str(workspace),
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=10,
        )
        if proc.returncode == 0 and proc.stdout.strip():
            return proc.stdout
        proc2 = subprocess.run(
            ["git", "diff"],
            cwd=str(workspace),
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=10,
        )
        return proc2.stdout or ""
    except Exception:
        return ""


def audit_diff_text(
    diff_text: str,
    allowed_files: Optional[List[str]] = None,
) -> Dict[str, Any]:
    findings: List[Dict[str, Any]] = []
    touched_files: List[str] = []
    current_file = ""
    removed_symbols: Dict[str, str] = {}
    added_symbols: Set[str] = set()
    added_lines_per_file: Dict[str, int] = {}

    for raw_ln in diff_text.splitlines():
        if raw_ln.startswith("+++ b/"):
            current_file = raw_ln[6:].strip()
            if current_file and current_file != "/dev/null" and current_file not in touched_files:
                touched_files.append(current_file)
            continue
        if raw_ln.startswith("--- ") or raw_ln.startswith("@@ ") or raw_ln.startswith("diff --git"):
            continue

        if raw_ln.startswith("+") and not raw_ln.startswith("+++"):
            code_ln = raw_ln[1:]
            added_lines_per_file[current_file] = added_lines_per_file.get(current_file, 0) + 1
            m_sym = SYMBOL_DEF_RE.search(code_ln)
            if m_sym:
                added_symbols.add(m_sym.group(1))
            for pat, reason in LAZINESS_PATTERNS:
                if pat.search(code_ln):
                    findings.append(
                        {
                            "kind": "laziness_placeholder",
                            "severity": "high",
                            "file": current_file or "diff",
                            "detail": f"{reason}: `{code_ln.strip()[:90]}`",
                        }
                    )
                    break

        elif raw_ln.startswith("-") and not raw_ln.startswith("---"):
            code_ln = raw_ln[1:]
            m_sym = SYMBOL_DEF_RE.search(code_ln)
            if m_sym:
                removed_symbols[m_sym.group(1)] = current_file or "diff"

    # Detect Silent Feature / Symbol Deletions
    for sym, fpath in removed_symbols.items():
        if sym not in added_symbols and not sym.startswith("_"):
            findings.append(
                {
                    "kind": "silent_feature_deletion",
                    "severity": "high",
                    "file": fpath,
                    "detail": f"Public symbol `{sym}` was deleted from `{fpath}` without replacement.",
                }
            )

    # Detect Out-of-Scope File Modifications (Karpathy Surgical Scope Law)
    if allowed_files:
        norm_allowed = [a.replace("\\", "/").strip("/") for a in allowed_files if a.strip()]
        for tf in touched_files:
            ntf = tf.replace("\\", "/")
            if not any(ntf == a or ntf.startswith(a + "/") or ntf.endswith("/" + a) for a in norm_allowed):
                findings.append(
                    {
                        "kind": "scope_creep",
                        "severity": "medium",
                        "file": tf,
                        "detail": f"`{tf}` modified outside declared surgical scope ({', '.join(norm_allowed)}).",
                    }
                )

    # Detect Over-Engineering / Monolith Bloat Spikes (>350 added lines in single file)
    for tf, cnt in added_lines_per_file.items():
        if cnt > 350 and not tf.endswith((".html", ".svg", ".md", ".json")):
            findings.append(
                {
                    "kind": "abstraction_bloat",
                    "severity": "low",
                    "file": tf,
                    "detail": f"`{tf}` added {cnt} lines in one diff — verify Karpathy Simplicity-First rule.",
                }
            )

    penalty = sum(25 if f["severity"] == "high" else (12 if f["severity"] == "medium" else 5) for f in findings)
    score = max(0, 100 - penalty)
    grade = "A+" if score >= 96 else ("A" if score >= 88 else ("B" if score >= 75 else ("C" if score >= 60 else "D")))

    return {
        "passed": all(f["severity"] != "high" for f in findings),
        "score": score,
        "grade": grade,
        "touched_files": touched_files,
        "finding_count": len(findings),
        "findings": findings,
    }


def verify_workspace_work(
    workspace: Path,
    diff_override: str = "",
    allowed_files: Optional[List[str]] = None,
) -> Dict[str, Any]:
    raw_diff = diff_override if diff_override.strip() else _get_git_diff(workspace.resolve())
    return audit_diff_text(raw_diff, allowed_files=allowed_files)


def render_markdown(rep: Dict[str, Any]) -> str:
    badge = "✅ PASSED" if rep["passed"] else "❌ BLOCKED BY KARPATHY GATE"
    lines = [
        f"### ⚖️ Karpathy Surgical Discipline Audit — {badge} (`{rep['score']}/100` • Grade `{rep['grade']}`)",
        f"- **Touched Files ({len(rep['touched_files'])}):** `{', '.join(rep['touched_files'][:8]) or 'none'}`",
    ]
    if not rep["findings"]:
        lines.append("- **Zero laziness placeholders, zero silent deletions, zero scope creep!**")
    else:
        for f in rep["findings"]:
            lines.append(f"- **[{f['severity'].upper()} • `{f['kind']}`]** `{f['file']}` — {f['detail']}")
    return "\n".join(lines)


def main() -> int:
    ap = argparse.ArgumentParser(description="Karpathy Surgical Diff & Anti-Laziness Auditor")
    ap.add_argument("--workspace", default=".")
    ap.add_argument("--diff-file", default="")
    ap.add_argument("--allowed-files", nargs="*", default=None)
    ap.add_argument("--json", action="store_true")
    ns = ap.parse_args()

    diff_txt = Path(ns.diff_file).read_text(encoding="utf-8") if ns.diff_file else ""
    rep = verify_workspace_work(Path(ns.workspace), diff_override=diff_txt, allowed_files=ns.allowed_files)
    print(json.dumps(rep, indent=2, ensure_ascii=False) if ns.json else render_markdown(rep))
    return 0 if rep["passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
