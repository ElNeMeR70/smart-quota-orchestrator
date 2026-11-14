#!/usr/bin/env python3
"""Generate an ultra-compact (<400 token) structured handoff brief from workspace & git state.

Eliminates redundant codebase re-discovery when compacting context (/compact),
switching model pools, or briefing fresh subagents/swarm workers.
Zero external dependencies (Python 3.8+ stdlib only).
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path
from typing import Any, Dict, List


def _configure_utf8() -> None:
    for stream in (sys.stdout, sys.stderr):
        if hasattr(stream, "reconfigure"):
            try:
                stream.reconfigure(encoding="utf-8")
            except Exception:
                pass


def _run_git(workspace: Path, args: List[str]) -> str:
    try:
        proc = subprocess.run(
            ["git", *args],
            cwd=str(workspace),
            capture_output=True,
            text=True,
            timeout=4,
            check=False,
        )
        return proc.stdout.strip() if proc.returncode == 0 else ""
    except Exception:
        return ""


def build_brief(workspace: Path, goal: str, next_steps: List[str]) -> Dict[str, Any]:
    branch = _run_git(workspace, ["rev-parse", "--abbrev-ref", "HEAD"]) or "(no-git)"
    last_commit = _run_git(workspace, ["log", "-1", "--oneline"]) or "(none)"
    status_lines = [ln for ln in _run_git(workspace, ["status", "--short"]).splitlines() if ln.strip()]
    diff_stat = _run_git(workspace, ["diff", "--stat", "HEAD"])

    top_entries = sorted(
        p.name + ("/" if p.is_dir() else "")
        for p in workspace.iterdir()
        if not p.name.startswith(".git") and p.name not in {"node_modules", "__pycache__", ".venv", "dist", "build"}
    )[:14]

    return {
        "workspace": str(workspace).replace("\\", "/"),
        "branch": branch,
        "last_commit": last_commit,
        "goal": goal or "Complete active implementation cleanly.",
        "modified_files": status_lines[:15],
        "modified_total": len(status_lines),
        "diff_stat_summary": diff_stat.splitlines()[-1].strip() if diff_stat else "Clean working tree",
        "top_level_layout": top_entries,
        "next_steps": next_steps or ["Run verification suite and finalize pending changes."],
    }


def render_markdown(data: Dict[str, Any]) -> str:
    lines = [
        "## Compact Handoff Brief",
        f"- **Workspace**: `{data['workspace']}` (`{data['branch']}` @ `{data['last_commit']}`)",
        f"- **Objective**: {data['goal']}",
        f"- **Diff Summary**: {data['diff_stat_summary']} (`{data['modified_total']}` dirty path(s))",
        f"- **Top Layout**: {', '.join(f'`{x}`' for x in data['top_level_layout'])}",
    ]
    if data["modified_files"]:
        lines.append("- **Active Files** *(do not re-scan unrelated dirs)*:")
        for item in data["modified_files"]:
            lines.append(f"  - `{item}`")
    lines.append("- **Next Atomic Actions**:")
    for idx, step in enumerate(data["next_steps"], start=1):
        lines.append(f"  {idx}. {step}")
    return "\n".join(lines)


def main() -> int:
    _configure_utf8()
    parser = argparse.ArgumentParser(description="Build a <400-token zero-loss handoff brief.")
    parser.add_argument("--workspace", "-w", default=".", help="Target workspace path.")
    parser.add_argument("--goal", "-g", default="", help="One-line summary of the active goal.")
    parser.add_argument("--next", "-n", nargs="*", default=[], help="Ordered list of remaining atomic steps.")
    parser.add_argument("--format", choices=("markdown", "json"), default="markdown", help="Output format.")
    args = parser.parse_args()

    brief = build_brief(Path(args.workspace).resolve(), args.goal, args.next)
    if args.format == "json":
        print(json.dumps(brief, indent=2, ensure_ascii=False))
    else:
        print(render_markdown(brief))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
