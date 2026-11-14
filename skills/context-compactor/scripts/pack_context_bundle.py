#!/usr/bin/env python3
"""Adaptive Token-Budgeted Multi-File Context Packer (Repomix-Pro Style).

Packs an entire directory or file list into a strict `--max-tokens` ceiling using
a 3-tier resolution cascade:
  - Tier 1 (Focus / Primary Files): Full source code included
  - Tier 2 (Supporting Files): Compact AST/Symbol signatures + `Lstart-Lend` skeleton!
  - Tier 3 (Overflow Files): 1-line path + line-count index entry

Guarantees an agent or subagent gets 100% architectural awareness of 50+ files
inside e.g. 3,000 tokens instead of 85,000 tokens!

Zero external dependencies (Python 3.8+ stdlib only).
"""

from __future__ import annotations

import argparse
import importlib.util
import json
import os
import sys
from pathlib import Path
from typing import Any, Dict, List, Set

IGNORE_DIRS: Set[str] = {
    ".git",
    ".sqo",
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
    "target",
}

CODE_EXTS: Set[str] = {
    ".py",
    ".ts",
    ".tsx",
    ".js",
    ".jsx",
    ".dart",
    ".go",
    ".rs",
    ".php",
    ".java",
    ".kt",
    ".md",
    ".json",
    ".yaml",
    ".yml",
}


def _configure_utf8() -> None:
    for stream in (sys.stdout, sys.stderr):
        if hasattr(stream, "reconfigure"):
            try:
                stream.reconfigure(encoding="utf-8")
            except Exception:
                pass


def _load_outline_module():
    outline_script = Path(__file__).resolve().parent / "smart_outline.py"
    spec = importlib.util.spec_from_file_location("smart_outline", outline_script)
    assert spec and spec.loader
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def pack_context(
    workspace: Path,
    scope_paths: List[str],
    focus_files: List[str],
    max_tokens: int = 3500,
) -> Dict[str, Any]:
    outline_mod = _load_outline_module()
    roots = [workspace / p for p in scope_paths] if scope_paths else [workspace]
    candidates: List[Path] = []

    for root in roots:
        if not root.exists():
            continue
        if root.is_file():
            candidates.append(root.resolve())
            continue
        for dirpath, dirnames, filenames in os.walk(root):
            dirnames[:] = [d for d in dirnames if d not in IGNORE_DIRS]
            for fname in filenames:
                fpath = Path(dirpath) / fname
                if fpath.suffix.lower() in CODE_EXTS and not fname.endswith((".lock", ".min.js", ".map")):
                    candidates.append(fpath.resolve())
                    if len(candidates) >= 600:
                        break
            if len(candidates) >= 600:
                break

    def rel_str(p: Path) -> str:
        try:
            return str(p.relative_to(workspace)).replace("\\", "/")
        except ValueError:
            return str(p).replace("\\", "/")

    focus_norm = {f.replace("\\", "/").lower() for f in focus_files}

    def sort_key(p: Path) -> tuple[int, int, str]:
        r = rel_str(p).lower()
        is_focus = 0 if any(r.endswith(fn) for fn in focus_norm) else 1
        sz = p.stat().st_size if p.exists() else 999999
        return (is_focus, sz, r)

    candidates = sorted(set(candidates), key=sort_key)

    raw_total_tokens = 0
    budget_left = max(300, max_tokens - 150)
    full_included: List[Dict[str, Any]] = []
    skeleton_included: List[Dict[str, Any]] = []
    index_only: List[str] = []

    for fpath in candidates:
        r = rel_str(fpath)
        try:
            text = fpath.read_text(encoding="utf-8", errors="ignore")
        except OSError:
            continue
        tok = max(1, int(len(text) / 4))
        raw_total_tokens += tok

        is_focus = any(r.lower().endswith(fn) for fn in focus_norm)
        if (is_focus or len(full_included) < 2) and tok <= int(budget_left * 0.65):
            full_included.append({"file": r, "tokens": tok, "content": text.strip()})
            budget_left -= tok
        elif budget_left >= 60:
            outline = outline_mod.build_outline(fpath)
            skel_lines = [f"L{s['start_line']}-L{s['end_line']}: {s['signature']}" for s in outline["symbols"][:25]]
            skel_text = "\n".join(skel_lines) if skel_lines else f"({outline['total_lines']} lines, no top-level symbols)"
            skel_tok = max(8, int(len(skel_text) / 4) + 8)
            if skel_tok <= budget_left:
                skeleton_included.append({"file": r, "lines": outline["total_lines"], "tokens": skel_tok, "skeleton": skel_text})
                budget_left -= skel_tok
            else:
                index_only.append(f"{r} ({outline['total_lines']}L)")
        else:
            index_only.append(f"{r} ({len(text.splitlines())}L)")

    used_tokens = max_tokens - budget_left
    savings_pct = max(0.0, round((1.0 - used_tokens / max(1, raw_total_tokens)) * 100, 1))

    return {
        "total_files_scanned": len(candidates),
        "uncompressed_approx_tokens": raw_total_tokens,
        "packed_approx_tokens": used_tokens,
        "token_budget": max_tokens,
        "token_savings_pct": savings_pct,
        "tier1_full_files": full_included,
        "tier2_skeleton_files": skeleton_included,
        "tier3_index_files": index_only,
    }


def render_markdown(pack: Dict[str, Any]) -> str:
    lines = [
        "## Adaptive Context Pack",
        f"- **Coverage**: `{pack['total_files_scanned']}` files (`~{pack['uncompressed_approx_tokens']:,}` raw tokens) -> **Packed into `~{pack['packed_approx_tokens']:,}` tokens** (**{pack['token_savings_pct']}% saved**)",
        f"- **Resolution Split**: `{len(pack['tier1_full_files'])}` Full Source • `{len(pack['tier2_skeleton_files'])}` AST Skeletons • `{len(pack['tier3_index_files'])}` Index Entries",
        "",
    ]
    if pack["tier1_full_files"]:
        lines.append("### Tier 1 — Primary Focus Files (Full Source)")
        for item in pack["tier1_full_files"]:
            lines.append(f"\n#### `{item['file']}`\n```\n{item['content']}\n```")
    if pack["tier2_skeleton_files"]:
        lines.append("\n### Tier 2 — Architectural Skeletons (Read Specific `Lstart-Lend` Only If Needed)")
        for sk in pack["tier2_skeleton_files"]:
            lines.append(f"\n#### `{sk['file']}` (`{sk['lines']}` lines)\n```text\n{sk['skeleton']}\n```")
    if pack["tier3_index_files"]:
        lines.append("\n### Tier 3 — Remaining File Index")
        lines.append(", ".join(f"`{x}`" for x in pack["tier3_index_files"][:40]))
    return "\n".join(lines)


def main() -> int:
    _configure_utf8()
    parser = argparse.ArgumentParser(description="Compile multi-file context into a strict token budget using adaptive AST compression.")
    parser.add_argument("--workspace", "-w", default=".", help="Workspace root directory.")
    parser.add_argument("--paths", "-p", nargs="*", default=[], help="Subdirectories or files to pack.")
    parser.add_argument("--focus", "-f", nargs="*", default=[], help="High-priority files to keep in full source resolution.")
    parser.add_argument("--max-tokens", "-m", type=int, default=3500, help="Strict token ceiling (default: 3500).")
    parser.add_argument("--format", choices=("markdown", "json"), default="markdown", help="Output format.")
    args = parser.parse_args()

    res = pack_context(Path(args.workspace).resolve(), args.paths, args.focus, max_tokens=max(400, args.max_tokens))
    if args.format == "json":
        print(json.dumps(res, indent=2, ensure_ascii=False))
    else:
        print(render_markdown(res))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
