#!/usr/bin/env python3
"""Token-Budgeted Semantic Git Diff Compressor.

Prevents massive `git diff` outputs (lockfiles, generated bundles, SVG dumps,
formatting churn) from consuming 20,000+ context tokens during code review or PR prep.
Automatically strips lockfiles/generated artifacts, scores changed files by logic/security
priority, and fits the output cleanly within `--max-tokens` (default: 2000).

Zero external dependencies (Python 3.8+ stdlib only).
"""

from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from pathlib import Path
from typing import Any, Dict, List

SKIP_FILE_PATTERNS = (
    "package-lock.json",
    "pnpm-lock.yaml",
    "yarn.lock",
    "bun.lockb",
    "composer.lock",
    "pubspec.lock",
    "Cargo.lock",
    "poetry.lock",
    "uv.lock",
    ".min.js",
    ".min.css",
    ".map",
    ".snap",
    ".svg",
)

PRIORITY_KEYWORDS = ("auth", "security", "token", "payment", "stripe", "webhook", "db", "schema", "migration", "api", "route", "rules")


def _configure_utf8() -> None:
    for stream in (sys.stdout, sys.stderr):
        if hasattr(stream, "reconfigure"):
            try:
                stream.reconfigure(encoding="utf-8")
            except Exception:
                pass


def _run_git_diff(workspace: Path, target_ref: str, staged: bool) -> str:
    cmd = ["git", "diff", "--no-color", "-U2"]
    if staged:
        cmd.append("--staged")
    elif target_ref:
        cmd.append(target_ref)
    proc = subprocess.run(cmd, cwd=str(workspace), capture_output=True, text=True, errors="ignore", check=False)
    return proc.stdout


def _split_file_diffs(raw_diff: str) -> List[Dict[str, Any]]:
    chunks: List[Dict[str, Any]] = []
    if not raw_diff.strip():
        return chunks

    parts = re.split(r"(?=^diff --git )", raw_diff, flags=re.MULTILINE)
    for part in parts:
        if not part.strip():
            continue
        header_match = re.match(r"^diff --git a/(.+?) b/(.+?)$", part, flags=re.MULTILINE)
        fname = header_match.group(2) if header_match else "unknown"
        added = sum(1 for ln in part.splitlines() if ln.startswith("+") and not ln.startswith("+++"))
        removed = sum(1 for ln in part.splitlines() if ln.startswith("-") and not ln.startswith("---"))
        skipped = any(fname.endswith(pat) or pat in fname for pat in SKIP_FILE_PATTERNS)

        fname_lower = fname.lower()
        priority = 10 if any(k in fname_lower for k in PRIORITY_KEYWORDS) else 5
        if fname_lower.endswith((".md", ".txt", ".json", ".lock")):
            priority = min(priority, 2)

        chunks.append({
            "file": fname,
            "added": added,
            "removed": removed,
            "skipped_generated": skipped,
            "priority": priority,
            "raw": part.strip(),
            "approx_tokens": max(1, int(len(part) / 4)),
        })
    return chunks


def compress_diff(raw_diff: str, max_tokens: int = 2000) -> Dict[str, Any]:
    raw_tokens = int(len(raw_diff) / 4)
    chunks = _split_file_diffs(raw_diff)
    skipped_files = [c for c in chunks if c["skipped_generated"]]
    active_files = sorted(
        [c for c in chunks if not c["skipped_generated"]],
        key=lambda c: (-c["priority"], c["approx_tokens"]),
    )

    budget_left = max(250, max_tokens - 180)
    included: List[Dict[str, Any]] = []
    summarized_only: List[Dict[str, Any]] = []

    for item in active_files:
        if item["approx_tokens"] <= budget_left:
            included.append({"file": item["file"], "added": item["added"], "removed": item["removed"], "diff": item["raw"]})
            budget_left -= item["approx_tokens"]
        elif budget_left >= 120:
            char_cap = budget_left * 4
            trimmed = item["raw"][:char_cap] + "\n... [truncated hunk to fit token budget; inspect file directly for remainder]"
            included.append({"file": item["file"], "added": item["added"], "removed": item["removed"], "diff": trimmed})
            budget_left = 0
        else:
            summarized_only.append({"file": item["file"], "added": item["added"], "removed": item["removed"]})

    return {
        "total_changed_files": len(chunks),
        "raw_diff_approx_tokens": raw_tokens,
        "token_budget": max_tokens,
        "skipped_lock_or_generated": [{"file": c["file"], "added": c["added"], "removed": c["removed"]} for c in skipped_files],
        "included_diffs": included,
        "summarized_overflow_files": summarized_only,
    }


def render_markdown(res: Dict[str, Any]) -> str:
    if res["total_changed_files"] == 0:
        return "## Compressed Git Diff\n- Working tree diff is empty."

    lines = [
        "## Token-Budgeted Git Diff",
        f"- **Changed Files**: `{res['total_changed_files']}` | **Raw Diff**: `~{res['raw_diff_approx_tokens']:,}` tokens -> **Capped at**: `<={res['token_budget']:,}` tokens",
    ]
    if res["skipped_lock_or_generated"]:
        skipped_str = ", ".join(f"`{x['file']}` (+{x['added']}/-{x['removed']})" for x in res["skipped_lock_or_generated"])
        lines.append(f"- **Auto-Stripped Noise/Lockfiles**: {skipped_str}")
    if res["summarized_overflow_files"]:
        over_str = ", ".join(f"`{x['file']}` (+{x['added']}/-{x['removed']})" for x in res["summarized_overflow_files"])
        lines.append(f"- **Stat-Only (Overflow)**: {over_str}")
    lines.append("")
    for item in res["included_diffs"]:
        lines.append(f"### `{item['file']}` (`+{item['added']} / -{item['removed']}`)")
        lines.append(f"```diff\n{item['diff']}\n```")
    return "\n".join(lines)


def main() -> int:
    _configure_utf8()
    parser = argparse.ArgumentParser(description="Compress git diff output into a strict token budget.")
    parser.add_argument("--workspace", "-w", default=".", help="Git repository path.")
    parser.add_argument("--ref", "-r", default="HEAD", help="Git ref to diff against (default: HEAD).")
    parser.add_argument("--staged", action="store_true", help="Diff staged changes only.")
    parser.add_argument("--max-tokens", "-m", type=int, default=2000, help="Maximum output token budget (default: 2000).")
    parser.add_argument("--stdin", action="store_true", help="Read raw diff text from stdin instead of invoking git.")
    parser.add_argument("--format", choices=("markdown", "json"), default="markdown", help="Output format.")
    args = parser.parse_args()

    raw = sys.stdin.read() if args.stdin else _run_git_diff(Path(args.workspace).resolve(), args.ref, args.staged)
    result = compress_diff(raw, max_tokens=args.max_tokens)
    if args.format == "json":
        print(json.dumps(result, indent=2, ensure_ascii=False))
    else:
        print(render_markdown(result))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
