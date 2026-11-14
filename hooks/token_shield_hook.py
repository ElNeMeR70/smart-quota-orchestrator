#!/usr/bin/env python3
"""Autonomous `PreToolUse` Token-Bomb & Lockfile Interceptor Hook (<15ms).

Protects agent sessions in real time BEFORE catastrophic token floods happen:
  1. Intercepts `read_file` / `view_file` calls targeting giant generated lockfiles,
     `.map` sourcemaps, or `.min.js` bundles (>60 KB) when no tight line range is set.
  2. Intercepts `run_command` calls that `cat` / `type` / `Get-Content` whole
     lockfiles or sourcemaps without `head` / `Select-Object -First`.

Always fails open (`{"decision": "allow"}`) on any unexpected payload so legitimate
workflows are never disrupted.
Zero external dependencies (Python 3.8+ stdlib only).
"""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path
from typing import Any, Dict

BOMB_FILENAMES = {
    "package-lock.json",
    "pnpm-lock.yaml",
    "yarn.lock",
    "bun.lockb",
    "composer.lock",
    "pubspec.lock",
    "cargo.lock",
    "poetry.lock",
    "uv.lock",
}

BOMB_SUFFIXES = (".min.js", ".min.css", ".bundle.js", ".js.map", ".css.map", ".har")

SHELL_DUMP_RE = re.compile(
    r"\b(?:cat|type|get-content|gc)\b[^|;\n]*\b(?:package-lock\.json|pnpm-lock\.yaml|yarn\.lock|composer\.lock|pubspec\.lock|Cargo\.lock|[A-Za-z0-9_.-]+\.(?:min\.js|map|har))\b",
    re.IGNORECASE,
)
SHELL_BOUNDED_RE = re.compile(r"\b(?:head|tail|select-object|select-string|grep|rg|wc|measure-object)\b", re.IGNORECASE)


def evaluate_hook(payload: Dict[str, Any]) -> Dict[str, Any]:
    tool_call = payload.get("toolCall") or {}
    tool_name = str(tool_call.get("name") or "").lower()
    args = tool_call.get("args") or {}
    if not isinstance(args, dict):
        return {"decision": "allow"}

    # 1. Guard file-reading tools against generated lockfile / sourcemap token bombs
    if tool_name in {"read_file", "view_file"}:
        raw_path = str(args.get("Path") or args.get("AbsolutePath") or args.get("file_path") or "")
        if not raw_path:
            return {"decision": "allow"}

        p = Path(raw_path)
        fname_lower = p.name.lower()
        start_ln = args.get("StartLine")
        end_ln = args.get("EndLine")
        has_tight_range = (
            isinstance(start_ln, int)
            and isinstance(end_ln, int)
            and 0 < (end_ln - start_ln) <= 150
        )

        is_bomb_type = fname_lower in BOMB_FILENAMES or fname_lower.endswith(BOMB_SUFFIXES)
        if is_bomb_type and not has_tight_range:
            try:
                sz_kb = round(p.stat().st_size / 1024, 1) if p.is_file() else 999.0
            except OSError:
                sz_kb = 999.0
            if sz_kb >= 50.0:
                return {
                    "decision": "deny",
                    "reason": (
                        f"[Smart Quota Shield] Blocked full read of generated artifact `{p.name}` ({sz_kb} KB) "
                        "to prevent massive context token waste. Read the primary manifest (`package.json`, "
                        "`pubspec.yaml`, `pyproject.toml`) or pass a tight `StartLine`–`EndLine` range (<=150 lines)."
                    ),
                }

    # 2. Guard shell commands against raw `cat package-lock.json` dumps
    if tool_name == "run_command":
        cmd = str(args.get("CommandLine") or args.get("command") or "")
        if cmd and SHELL_DUMP_RE.search(cmd) and not SHELL_BOUNDED_RE.search(cmd):
            return {
                "decision": "deny",
                "reason": (
                    "[Smart Quota Shield] Blocked unbounded terminal dump of a lockfile/sourcemap/bundle. "
                    "Pipe through `rg`, `head -n 40`, or `Select-Object -First 40` instead."
                ),
            }

    return {"decision": "allow"}


def main() -> int:
    try:
        raw = sys.stdin.read()
        payload = json.loads(raw) if raw.strip() else {}
        decision = evaluate_hook(payload)
    except Exception:
        decision = {"decision": "allow"}

    sys.stdout.write(json.dumps(decision) + "\n")
    sys.stdout.flush()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
