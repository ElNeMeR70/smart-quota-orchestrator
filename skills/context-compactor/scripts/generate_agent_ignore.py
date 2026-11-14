#!/usr/bin/env python3
"""Context-Bomb Scanner & `.agentignore` / `.cursorignore` / `.claudeignore` Generator.

Scans a project for heavy generated files, sourcemaps, lockfiles, SQL/JSON dumps,
minified bundles, and build artifacts that silently poison AI agent searches and
burn tens of thousands of tokens per accidental read.

Use `--write` to generate or update `.agentignore` (or `--target .cursorignore` / `.claudeignore`).
Zero external dependencies (Python 3.8+ stdlib only).
"""

from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path
from typing import Any, Dict, List, Set

DEFAULT_SKIP_WALK: Set[str] = {".git", ".sqo"}
BINARY_NON_TEXT_EXTS: Set[str] = {".png", ".jpg", ".jpeg", ".webp", ".gif", ".ico", ".woff", ".woff2", ".ttf", ".mp4", ".mp3"}

STANDARD_IGNORE_PATTERNS: List[str] = [
    "# Dependencies & package caches",
    "node_modules/",
    "vendor/",
    ".venv/",
    "venv/",
    "__pycache__/",
    ".dart_tool/",
    "",
    "# Build, bundle & coverage outputs",
    "dist/",
    "build/",
    ".next/",
    "out/",
    "coverage/",
    "target/",
    "*.min.js",
    "*.min.css",
    "*.map",
    "",
    "# Lockfiles (zero architectural signal, huge token weight)",
    "package-lock.json",
    "pnpm-lock.yaml",
    "yarn.lock",
    "bun.lockb",
    "composer.lock",
    "pubspec.lock",
    "Cargo.lock",
    "poetry.lock",
    "uv.lock",
    "",
    "# Data dumps, logs & heavy media",
    "*.log",
    "*.sql",
    "*.sqlite",
    "*.db",
    "*.har",
]

TOKEN_BOMB_EXTS = {".map", ".sql", ".har", ".log", ".csv", ".lock", ".svg"}


def _configure_utf8() -> None:
    for stream in (sys.stdout, sys.stderr):
        if hasattr(stream, "reconfigure"):
            try:
                stream.reconfigure(encoding="utf-8")
            except Exception:
                pass


def scan_token_bombs(workspace: Path, size_threshold_kb: int = 80) -> Dict[str, Any]:
    bombs: List[Dict[str, Any]] = []
    detected_heavy_dirs: Set[str] = set()
    threshold_bytes = size_threshold_kb * 1024

    heavy_dir_names = {"node_modules", "vendor", ".next", "dist", "build", "coverage", ".venv", "venv", "target", ".dart_tool"}

    for dirpath, dirnames, filenames in os.walk(workspace):
        kept_dirs: List[str] = []
        for d in dirnames:
            if d in DEFAULT_SKIP_WALK:
                continue
            if d in heavy_dir_names:
                rel_d = str((Path(dirpath) / d).relative_to(workspace)).replace("\\", "/") + "/"
                detected_heavy_dirs.add(rel_d)
                continue
            kept_dirs.append(d)
        dirnames[:] = kept_dirs

        for fname in filenames:
            fpath = Path(dirpath) / fname
            try:
                sz = fpath.stat().st_size
            except OSError:
                continue

            ext = fpath.suffix.lower()
            if ext in BINARY_NON_TEXT_EXTS:
                continue
            is_minified = fname.endswith((".min.js", ".min.css", ".bundle.js"))
            if sz >= threshold_bytes or is_minified or (ext in TOKEN_BOMB_EXTS and sz >= 20 * 1024):
                rel = str(fpath.relative_to(workspace)).replace("\\", "/")
                bombs.append({
                    "file": rel,
                    "size_kb": round(sz / 1024, 1),
                    "approx_tokens_if_read": int(sz / 4),
                    "reason": "minified/sourcemap" if (is_minified or ext == ".map") else ("lockfile/dump" if ext in TOKEN_BOMB_EXTS else "oversized_file"),
                })

    bombs.sort(key=lambda x: -x["size_kb"])
    custom_rules = list(STANDARD_IGNORE_PATTERNS)
    extra_specific = [b["file"] for b in bombs[:15] if b["reason"] == "oversized_file"]
    if extra_specific:
        custom_rules.append("")
        custom_rules.append("# Workspace-specific oversized files detected by sqo ignore-guard")
        custom_rules.extend(extra_specific)

    return {
        "workspace": str(workspace).replace("\\", "/"),
        "heavy_directories_found": sorted(detected_heavy_dirs),
        "token_bomb_files_count": len(bombs),
        "total_preventable_tokens": sum(b["approx_tokens_if_read"] for b in bombs),
        "top_token_bombs": bombs[:15],
        "generated_ignore_content": "\n".join(custom_rules) + "\n",
    }


def render_markdown(rep: Dict[str, Any], written_to: str = "") -> str:
    lines = [
        "## Context-Bomb & Ignore-Guard Scan",
        f"- **Heavy Directories Shielded**: `{len(rep['heavy_directories_found'])}` ({', '.join(f'`{d}`' for d in rep['heavy_directories_found'][:6]) or 'None'})",
        f"- **Token-Bomb Files Detected**: `{rep['token_bomb_files_count']}` file(s) (`~{rep['total_preventable_tokens']:,}` preventable tokens)",
    ]
    if written_to:
        lines.append(f"- **Written Ignore File**: `{written_to}` ✅")
    if rep["top_token_bombs"]:
        lines.extend(["", "### Top Token-Bomb Files", ""])
        for b in rep["top_token_bombs"][:10]:
            lines.append(f"- `{b['file']}` — `{b['size_kb']} KB` (`~{b['approx_tokens_if_read']:,}` tokens, {b['reason']})")
    else:
        lines.append("\n- Workspace is clean — zero oversized context-bomb files detected!")
    return "\n".join(lines)


def main() -> int:
    _configure_utf8()
    parser = argparse.ArgumentParser(description="Detect context-poisoning heavy files and generate .agentignore / .cursorignore / .claudeignore.")
    parser.add_argument("--workspace", "-w", default=".", help="Target workspace directory.")
    parser.add_argument("--threshold-kb", type=int, default=80, help="File size threshold in KB (default: 80).")
    parser.add_argument("--write", action="store_true", help="Write the generated ignore rules to disk.")
    parser.add_argument("--target", default=".agentignore", help="Ignore filename when --write is set (e.g., .agentignore, .cursorignore, .claudeignore).")
    parser.add_argument("--format", choices=("markdown", "json"), default="markdown", help="Output format.")
    args = parser.parse_args()

    ws = Path(args.workspace).resolve()
    rep = scan_token_bombs(ws, size_threshold_kb=args.threshold_kb)
    written_path = ""
    if args.write:
        out_file = ws / args.target
        out_file.write_text(rep["generated_ignore_content"], encoding="utf-8")
        written_path = str(out_file).replace("\\", "/")

    if args.format == "json":
        print(json.dumps(rep, indent=2, ensure_ascii=False))
    else:
        print(render_markdown(rep, written_to=written_path))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
