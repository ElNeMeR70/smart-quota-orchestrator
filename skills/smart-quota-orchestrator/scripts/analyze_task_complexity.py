#!/usr/bin/env python3
"""Deterministic task & workspace complexity scorer for quota-aware agent routing.

Evaluates target files/directories, lines of code, domain risk signals (auth,
crypto, billing, migrations, concurrency), and module independence to compute:
  - Complexity Score (0-100)
  - Parallelizability Index (0.0-1.0)
  - Recommended Model Tier & Multi-Agent Topology
  - Estimated Quota Savings vs. Monolithic Frontier Execution

Zero external dependencies (Python 3.8+ stdlib only).
"""

from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
import sys
from pathlib import Path
from typing import Any, Dict, List, Set

IGNORE_DIRS: Set[str] = {
    ".git",
    "node_modules",
    ".next",
    "dist",
    "build",
    "out",
    "coverage",
    "__pycache__",
    ".venv",
    "venv",
    "vendor",
    ".dart_tool",
    ".idea",
    ".vscode",
    "target",
}

CODE_EXTENSIONS: Set[str] = {
    ".py",
    ".ts",
    ".tsx",
    ".js",
    ".jsx",
    ".mjs",
    ".cjs",
    ".dart",
    ".go",
    ".rs",
    ".java",
    ".kt",
    ".swift",
    ".php",
    ".rb",
    ".cs",
    ".cpp",
    ".c",
    ".h",
    ".sql",
    ".vue",
    ".svelte",
    ".css",
    ".scss",
    ".html",
    ".yaml",
    ".yml",
    ".json",
    ".md",
}

HIGH_RISK_KEYWORDS: Dict[str, List[str]] = {
    "security_auth": ["auth", "jwt", "oauth", "token", "password", "rbac", "permission", "firestore.rules", "cors", "csp", "crypto", "secret"],
    "payments_billing": ["stripe", "payment", "webhook", "billing", "invoice", "wallet", "ledger", "checkout"],
    "data_migration": ["migration", "schema", "prisma", "alembic", "alter table", "drop ", "transaction"],
    "concurrency_infra": ["race", "mutex", "deadlock", "worker", "queue", "websocket", "cluster", "docker", "k8s"],
}

BATCH_KEYWORDS: List[str] = [
    "all files",
    "every ",
    "across the repo",
    "audit",
    "scan",
    "migrate all",
    "translate",
    "i18n",
    "rtl",
    "lint",
    "unit tests for",
    "refactor all",
]


def _configure_utf8() -> None:
    for stream in (sys.stdout, sys.stderr):
        if hasattr(stream, "reconfigure"):
            try:
                stream.reconfigure(encoding="utf-8")
            except Exception:
                pass


def _git_changed_files(workspace: Path) -> List[str]:
    try:
        proc = subprocess.run(
            ["git", "status", "--porcelain"],
            cwd=str(workspace),
            capture_output=True,
            text=True,
            timeout=4,
            check=False,
        )
        if proc.returncode != 0:
            return []
        changed: List[str] = []
        for line in proc.stdout.splitlines():
            if len(line) > 3:
                changed.append(line[3:].strip())
        return changed
    except Exception:
        return []


def _scan_paths(workspace: Path, target_paths: List[str], max_files: int = 1500) -> Dict[str, Any]:
    roots = [workspace / p for p in target_paths] if target_paths else [workspace]
    total_files = 0
    total_loc = 0
    top_modules: Set[str] = set()
    ext_counts: Dict[str, int] = {}
    large_files: List[Dict[str, Any]] = []

    for root in roots:
        if not root.exists():
            continue
        if root.is_file():
            files_iter = [root]
        else:
            files_iter = []
            for dirpath, dirnames, filenames in os.walk(root):
                dirnames[:] = [d for d in dirnames if d not in IGNORE_DIRS]
                for fname in filenames:
                    files_iter.append(Path(dirpath) / fname)
                    if len(files_iter) >= max_files:
                        break
                if len(files_iter) >= max_files:
                    break

        for fpath in files_iter:
            ext = fpath.suffix.lower()
            if ext not in CODE_EXTENSIONS:
                continue
            total_files += 1
            ext_counts[ext] = ext_counts.get(ext, 0) + 1
            try:
                rel = fpath.relative_to(workspace)
                parts = rel.parts
                if len(parts) > 1:
                    top_modules.add(parts[0] if parts[0] != "src" or len(parts) == 2 else f"src/{parts[1]}")
                else:
                    top_modules.add("(root)")
            except ValueError:
                rel = fpath
                top_modules.add(fpath.parent.name or "(root)")

            try:
                with open(fpath, "r", encoding="utf-8", errors="ignore") as fh:
                    loc = sum(1 for _ in fh)
                total_loc += loc
                if loc >= 450:
                    large_files.append({"file": str(rel).replace("\\", "/"), "loc": loc})
            except OSError:
                pass

    large_files.sort(key=lambda item: -item["loc"])
    return {
        "total_code_files": total_files,
        "total_loc": total_loc,
        "distinct_modules": sorted(top_modules),
        "extensions": dict(sorted(ext_counts.items(), key=lambda kv: -kv[1])[:8]),
        "large_files": large_files[:8],
    }


def evaluate_task(workspace: Path, task: str, paths: List[str]) -> Dict[str, Any]:
    scan = _scan_paths(workspace, paths)
    git_dirty = _git_changed_files(workspace)
    task_lower = (task or "").lower()

    triggered_risks: List[str] = []
    for category, words in HIGH_RISK_KEYWORDS.items():
        if any(w in task_lower for w in words):
            triggered_risks.append(category)

    is_batch_intent = any(kw in task_lower for kw in BATCH_KEYWORDS)

    # Compute deterministic Complexity Score (0-100)
    files_n = scan["total_code_files"]
    loc_n = scan["total_loc"]
    mod_n = len(scan["distinct_modules"])

    file_score = min(28, int(files_n * 1.4)) if paths else min(22, int(min(files_n, 80) * 0.28))
    loc_score = min(22, int(loc_n / 450))
    risk_score = min(30, len(triggered_risks) * 14)
    scope_words = len(re.findall(r"\b(and|also|plus|integrate|refactor|architect|end-to-end|full-stack)\b", task_lower))
    intent_score = min(20, scope_words * 5 + (10 if is_batch_intent else 0))

    complexity = max(8, min(100, file_score + loc_score + risk_score + intent_score))

    # Compute Parallelizability Index (0.0 - 1.0)
    raw_parallel = 0.15
    if mod_n >= 3:
        raw_parallel += min(0.45, mod_n * 0.1)
    if is_batch_intent:
        raw_parallel += 0.35
    if files_n <= 2 and not is_batch_intent:
        raw_parallel = 0.1
    parallel_idx = round(min(1.0, raw_parallel), 2)

    # Select Topology & Model Tier
    if complexity <= 25:
        topology = "Direct Inline Execution (Single Agent)"
        tier = "Gemini 4 Hydrogen (Low/Medium) or Current Model (Low)"
        workflow_mode = "direct"
        savings_est = "60-75% vs standalone frontier model"
    elif complexity <= 60 and parallel_idx >= 0.5:
        topology = "run_workflow Parallel Fan-Out (Map-Reduce)"
        tier = "Planner: Current/Argon | Workers: model='flash' or 'flash_lite'"
        workflow_mode = "run_workflow"
        savings_est = "55-70% (avoids loading all files into main context)"
    elif complexity <= 60:
        topology = "Staged Single-Agent Edit (Grep -> Line-Range Read -> Edit)"
        tier = "Orchestrator (Argon) or Gemini 4 Argon (Medium)"
        workflow_mode = "staged_single"
        savings_est = "40-55% vs standalone Carbon"
    elif parallel_idx >= 0.55:
        topology = "Interface-First Parallel Worktrees (run_workflow / Lean Swarm)"
        tier = "Orchestrator (Carbon) + Isolated Authors (workspace='share')"
        workflow_mode = "parallel_worktrees"
        savings_est = "45-60% (eliminates merge rework + isolates context)"
    else:
        topology = "Read-Only Recon Subagent -> Deep Architect Implementation"
        tier = "Orchestrator (Carbon) or Gemini 4 Carbon (High for security-critical steps)"
        workflow_mode = "recon_then_deep"
        savings_est = "35-50% (keeps raw search noise out of main context)"

    return {
        "task": task or "(workspace structural scan)",
        "complexity_score": complexity,
        "parallelizability_index": parallel_idx,
        "risk_domains": triggered_risks,
        "batch_fanout_detected": is_batch_intent,
        "workspace_metrics": {
            **scan,
            "git_modified_count": len(git_dirty),
        },
        "routing_decision": {
            "mode": workflow_mode,
            "recommended_topology": topology,
            "recommended_model_tier": tier,
            "estimated_quota_savings": savings_est,
        },
    }


def render_markdown(res: Dict[str, Any]) -> str:
    m = res["workspace_metrics"]
    r = res["routing_decision"]
    risks = ", ".join(f"`{x}`" for x in res["risk_domains"]) if res["risk_domains"] else "None detected"
    lines = [
        "## Pre-Flight Complexity & Quota Routing Plan",
        "",
        "| Metric | Value |",
        "| :--- | :--- |",
        f"| **Complexity Score** | **{res['complexity_score']} / 100** |",
        f"| **Parallelizability Index** | `{res['parallelizability_index']}` (0 = sequential, 1 = embarrassingly parallel) |",
        f"| **Scanned Code Files / LOC** | `{m['total_code_files']}` files / `{m['total_loc']}` lines across `{len(m['distinct_modules'])}` module(s) |",
        f"| **High-Risk Domains** | {risks} |",
        f"| **Optimal Topology** | **{r['recommended_topology']}** |",
        f"| **Recommended Model Tier** | `{r['recommended_model_tier']}` |",
        f"| **Estimated Quota Savings** | **{r['estimated_quota_savings']}** |",
    ]
    if m["large_files"]:
        lines.extend(["", "### Large Files Detected (Use Line-Range Reads Only!)", ""])
        for lf in m["large_files"][:5]:
            lines.append(f"- `{lf['file']}` (`{lf['loc']}` lines) — grep symbols first; avoid full-file dumps.")
    return "\n".join(lines)


def main() -> int:
    _configure_utf8()
    parser = argparse.ArgumentParser(
        description="Score task complexity and recommend the lowest-quota execution strategy."
    )
    parser.add_argument("--workspace", "-w", default=".", help="Workspace root directory (default: current dir).")
    parser.add_argument("--task", "-t", default="", help="Natural-language description of the user task.")
    parser.add_argument("--paths", "-p", nargs="*", default=[], help="Optional specific subdirectories or files to scope analysis.")
    parser.add_argument("--format", choices=("markdown", "json"), default="markdown", help="Output format.")
    args = parser.parse_args()

    result = evaluate_task(Path(args.workspace).resolve(), args.task, args.paths)
    if args.format == "json":
        print(json.dumps(result, indent=2, ensure_ascii=False))
    else:
        print(render_markdown(result))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
