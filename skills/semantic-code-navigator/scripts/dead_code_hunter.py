#!/usr/bin/env python3
"""Orphan Module & AI Dead-Code Hunter (`dead_code_hunter.py` — v13.0 Zenith Edition).

AI coding sessions frequently create helper modules or duplicate components during
refactors and leave old files unreferenced — silently inflating search noise and context tokens.

Cross-checks all source files against:
  1. Inbound import edges across Python, TS/JS, Dart, Go, and PHP
  2. Framework convention entrypoints (`main.*`, `index.*`, `page.tsx`, `layout.tsx`, `route.ts`, `routes/*.php`, `tests/*`, `scripts/*`)
Reports high-confidence orphan candidate files and estimated context tokens reclaimable!
"""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from typing import Any, Dict, List, Set

ENTRY_PATTERNS = re.compile(
    r"(?:^|/)(?:main|app|server|index|cli|sqo|mcp_server|extension|middleware|setup|manage|conftest|routes|page|layout|route|loading|error)\."
    r"|(?:^|/)(?:tests?|__tests__|spec|scripts|bin|hooks|migrations|pages|api|cmd)/"
    r"|\.(?:test|spec|d|config|stories)\.",
    re.IGNORECASE,
)

IMPORT_TOKEN_RE = re.compile(
    r"""(?:from\s+['"]?([A-Za-z0-9_./-]+)|import\s+['"]?([A-Za-z0-9_./-]+)|require\s*\(\s*['"]([A-Za-z0-9_./-]+)['"]\))"""
)

SKIP_DIRS = {".git", "node_modules", ".venv", "venv", "__pycache__", "build", "dist", ".next", ".dart_tool", "vendor", ".sqo"}
SOURCE_EXTS = {".py", ".ts", ".tsx", ".js", ".jsx", ".dart", ".go", ".php"}


def hunt_dead_modules(workspace: Path) -> Dict[str, Any]:
    workspace = workspace.resolve()
    files: List[Path] = []
    for p in workspace.rglob("*"):
        if not p.is_file() or p.suffix.lower() not in SOURCE_EXTS:
            continue
        if any(part in SKIP_DIRS for part in p.parts):
            continue
        files.append(p)
        if len(files) >= 1200:
            break

    referenced_stems: Set[str] = set()
    all_contents: Dict[str, str] = {}

    for p in files:
        rel = str(p.relative_to(workspace)).replace("\\", "/")
        try:
            txt = p.read_text(encoding="utf-8", errors="ignore")
        except OSError:
            continue
        all_contents[rel] = txt
        for m in IMPORT_TOKEN_RE.finditer(txt):
            raw_ref = (m.group(1) or m.group(2) or m.group(3) or "").strip()
            if raw_ref:
                leaf = raw_ref.replace(".", "/").split("/")[-1]
                if leaf:
                    referenced_stems.add(leaf.lower())

    # Second pass: check if stem appears anywhere in OTHER files (catches dynamic loaders)
    orphan_candidates: List[Dict[str, Any]] = []
    reclaimable_tokens = 0

    for rel, txt in sorted(all_contents.items()):
        if ENTRY_PATTERNS.search(rel):
            continue
        stem = Path(rel).stem
        if stem.startswith("__") or stem.lower() in referenced_stems:
            continue
        # Check literal stem mention in any other file
        mentioned_elsewhere = any(
            other_rel != rel and stem in other_txt
            for other_rel, other_txt in all_contents.items()
        )
        if not mentioned_elsewhere:
            tok = max(1, len(txt) // 4)
            reclaimable_tokens += tok
            orphan_candidates.append(
                {
                    "file": rel,
                    "lines": len(txt.splitlines()),
                    "approx_tokens": tok,
                }
            )

    return {
        "scanned_files": len(all_contents),
        "orphan_count": len(orphan_candidates),
        "reclaimable_tokens": reclaimable_tokens,
        "orphan_candidates": orphan_candidates[:30],
    }


def render_markdown(rep: Dict[str, Any]) -> str:
    lines = [
        f"### 🧹 Dead-Code & Orphan Module Hunter (`{rep['orphan_count']}` candidates across `{rep['scanned_files']}` files)",
        f"- **Reclaimable Context Bloat:** `~{rep['reclaimable_tokens']:,}` tokens",
    ]
    for c in rep["orphan_candidates"]:
        lines.append(f"- `{c['file']}` (`{c['lines']}` lines • `~{c['approx_tokens']}` tok) — zero inbound imports or references")
    if not rep["orphan_candidates"]:
        lines.append("- ✅ **Zero orphaned source modules detected — repository graph is 100% lean!**")
    return "\n".join(lines)


def main() -> int:
    ap = argparse.ArgumentParser(description="Hunt unreferenced orphan source modules")
    ap.add_argument("--workspace", "-w", default=".")
    ap.add_argument("--json", action="store_true")
    ns = ap.parse_args()
    rep = hunt_dead_modules(Path(ns.workspace))
    print(json.dumps(rep, indent=2, ensure_ascii=False) if ns.json else render_markdown(rep))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
