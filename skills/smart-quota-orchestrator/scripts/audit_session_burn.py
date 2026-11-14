#!/usr/bin/env python3
"""Audit AI agent JSONL session transcripts for token-draining anti-patterns.

Supports Google Antigravity (`transcript.jsonl`) and Claude Code (`*.jsonl`)
session logs. Detects:
  1. Duplicate reads of unchanged files
  2. Oversized tool outputs flooding prompt history
  3. Consecutive error / retry thrashing loops
  4. Overall context bloat level & `/compact` readiness

Zero external dependencies (Python 3.8+ stdlib only).
"""

from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional


def _configure_utf8() -> None:
    for stream in (sys.stdout, sys.stderr):
        if hasattr(stream, "reconfigure"):
            try:
                stream.reconfigure(encoding="utf-8")
            except Exception:
                pass


def _discover_latest_transcript() -> Optional[Path]:
    home = Path.home()
    candidates: List[Path] = []

    # 1. Antigravity brain transcripts
    agy_brain = home / ".gemini" / "antigravity" / "brain"
    if agy_brain.is_dir():
        for child in agy_brain.iterdir():
            t_file = child / ".system_generated" / "logs" / "transcript.jsonl"
            if t_file.is_file():
                candidates.append(t_file)

    # 2. Claude Code project transcripts
    claude_projects = home / ".claude" / "projects"
    if claude_projects.is_dir():
        for root, _, files in os.walk(claude_projects):
            for fname in files:
                if fname.endswith(".jsonl"):
                    candidates.append(Path(root) / fname)

    if not candidates:
        return None
    candidates.sort(key=lambda p: p.stat().st_mtime, reverse=True)
    return candidates[0]


def audit_transcript(path: Path) -> Dict[str, Any]:
    total_steps = 0
    error_steps = 0
    consecutive_errors = 0
    max_error_streak = 0
    total_chars = 0
    truncated_steps = 0

    file_reads: Dict[str, int] = {}
    edited_files_since_read: set[str] = set()
    redundant_reads: Dict[str, int] = {}
    heavy_steps: List[Dict[str, Any]] = []

    with open(path, "r", encoding="utf-8", errors="ignore") as fh:
        for line_no, raw in enumerate(fh, start=1):
            raw = raw.strip()
            if not raw:
                continue
            total_steps += 1
            total_chars += len(raw)
            try:
                entry = json.loads(raw)
            except json.JSONDecodeError:
                continue

            status = str(entry.get("status", "")).upper()
            if status == "ERROR":
                error_steps += 1
                consecutive_errors += 1
                max_error_streak = max(max_error_streak, consecutive_errors)
            else:
                consecutive_errors = 0

            if entry.get("truncated_fields"):
                truncated_steps += 1

            step_len = len(str(entry.get("content", ""))) + len(str(entry.get("thinking", "")))
            if step_len >= 12000:
                heavy_steps.append(
                    {
                        "step": entry.get("step_index", line_no),
                        "type": entry.get("type", "UNKNOWN"),
                        "approx_tokens": int(step_len / 4),
                    }
                )

            tool_calls = entry.get("tool_calls") or []
            if isinstance(tool_calls, list):
                for tc in tool_calls:
                    if not isinstance(tc, dict):
                        continue
                    t_name = str(tc.get("name") or tc.get("tool") or "").lower()
                    t_args = tc.get("arguments") or tc.get("args") or {}
                    if isinstance(t_args, str):
                        try:
                            t_args = json.loads(t_args)
                        except Exception:
                            t_args = {}
                    if not isinstance(t_args, dict):
                        continue

                    target_path = str(
                        t_args.get("Path")
                        or t_args.get("file_path")
                        or t_args.get("AbsolutePath")
                        or ""
                    )
                    if not target_path:
                        continue

                    if any(k in t_name for k in ("read_file", "view_file", "read")):
                        if target_path in file_reads and target_path not in edited_files_since_read:
                            redundant_reads[target_path] = redundant_reads.get(target_path, 0) + 1
                        file_reads[target_path] = file_reads.get(target_path, 0) + 1
                        edited_files_since_read.discard(target_path)
                    elif any(k in t_name for k in ("edit_file", "write_file", "replace", "write")):
                        edited_files_since_read.add(target_path)

    approx_session_tokens = int(total_chars / 4)
    if total_steps >= 80 or approx_session_tokens >= 90000 or truncated_steps >= 8:
        bloat_level = "HIGH — Compact Recommended"
    elif total_steps >= 40 or approx_session_tokens >= 45000:
        bloat_level = "MODERATE — Delegate Subtasks to Keep Lean"
    else:
        bloat_level = "LEAN — Healthy Session Context"

    actions: List[str] = []
    if redundant_reads:
        actions.append(
            f"Eliminate {sum(redundant_reads.values())} redundant file re-read(s): rely on earlier context or pass StartLine/EndLine."
        )
    if max_error_streak >= 3:
        actions.append(
            f"Detected an error retry streak of {max_error_streak} consecutive failed steps — diagnose root causes before re-running commands."
        )
    if "HIGH" in bloat_level:
        actions.append(
            "Session history is heavy: generate a handoff brief (`context-compactor` skill) and run `/compact` to stop re-paying context overhead on every turn."
        )
    if not actions:
        actions.append("No major token leaks detected in this session. Continue using targeted reads and subagent isolation.")

    return {
        "transcript_path": str(path),
        "total_steps": total_steps,
        "approx_transcript_tokens": approx_session_tokens,
        "error_steps": error_steps,
        "max_consecutive_errors": max_error_streak,
        "truncated_large_steps": truncated_steps,
        "bloat_status": bloat_level,
        "redundant_file_reads": redundant_reads,
        "heaviest_steps": heavy_steps[:5],
        "recommended_actions": actions,
    }


def render_markdown(report: Dict[str, Any]) -> str:
    lines = [
        "## Session Token-Burn & Context Hygiene Audit",
        "",
        "| Metric | Value |",
        "| :--- | :--- |",
        f"| **Context Status** | **{report['bloat_status']}** |",
        f"| **Total Trajectory Steps** | `{report['total_steps']}` |",
        f"| **Approx. Cumulative Payload** | `~{report['approx_transcript_tokens']:,}` tokens |",
        f"| **Failed Tool Steps / Max Streak** | `{report['error_steps']}` total / `{report['max_consecutive_errors']}` consecutive |",
        f"| **Oversized (Truncated) Outputs** | `{report['truncated_large_steps']}` |",
    ]

    if report["redundant_file_reads"]:
        lines.extend(["", "### Redundant Unchanged File Re-Reads", ""])
        for fpath, count in sorted(report["redundant_file_reads"].items(), key=lambda kv: -kv[1])[:6]:
            lines.append(f"- `{fpath}` — re-read `{count}` extra time(s) without intermediate edits")

    lines.extend(["", "### Actionable Quota Fixes", ""])
    for act in report["recommended_actions"]:
        lines.append(f"- {act}")
    return "\n".join(lines)


def main() -> int:
    _configure_utf8()
    parser = argparse.ArgumentParser(description="Audit session JSONL transcript for token leaks and context bloat.")
    parser.add_argument("--transcript", "-t", help="Explicit path to transcript.jsonl.")
    parser.add_argument("--auto", action="store_true", help="Auto-discover the most recently active session transcript.")
    parser.add_argument("--format", choices=("markdown", "json"), default="markdown", help="Output format.")
    args = parser.parse_args()

    target: Optional[Path] = Path(args.transcript) if args.transcript else (_discover_latest_transcript() if args.auto else None)
    if target is None or not target.is_file():
        parser.error("Provide --transcript <path> or --auto (when an Antigravity or Claude Code session log exists).")

    report = audit_transcript(target)
    if args.format == "json":
        print(json.dumps(report, indent=2, ensure_ascii=False))
    else:
        print(render_markdown(report))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
