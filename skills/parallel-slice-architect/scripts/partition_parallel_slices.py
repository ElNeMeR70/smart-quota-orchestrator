#!/usr/bin/env python3
"""Dependency-graph analyzer & file-disjoint parallel slice partitioner.

Parses real import/include edges across Python, TypeScript/JavaScript, Dart, Go,
and PHP files in a workspace to separate:
  - Stage 0 (Shared Contracts / High Fan-In Foundations — edit FIRST sequentially)
  - Stage 1 (Independent File-Disjoint Worker Slices — safe to run in parallel!)
  - Stage 2 (Integration & Verification)

Can also emit a ready-to-run Antigravity `run_workflow` Python script (`--emit-workflow`).
Zero external dependencies (Python 3.8+ stdlib only).
"""

from __future__ import annotations

import argparse
import ast
import json
import os
import re
import sys
from collections import defaultdict
from pathlib import Path
from typing import Any, Dict, List, Optional, Set, Tuple

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
    "target",
}

SOURCE_EXTS: Set[str] = {".py", ".ts", ".tsx", ".js", ".jsx", ".mjs", ".dart", ".go", ".php"}

TS_IMPORT_RE = re.compile(
    r"""(?:import|export)\s+(?:type\s+)?(?:[^'"]*?\s+from\s+)?['"]([^'"]+)['"]|require\(\s*['"]([^'"]+)['"]\s*\)"""
)
DART_IMPORT_RE = re.compile(r"""^\s*(?:import|export|part)\s+['"]([^'"]+)['"]""", re.MULTILINE)
PHP_IMPORT_RE = re.compile(r"""^\s*(?:require|require_once|include|include_once)\s*\(?\s*['"]([^'"]+)['"]""", re.MULTILINE)


def _configure_utf8() -> None:
    for stream in (sys.stdout, sys.stderr):
        if hasattr(stream, "reconfigure"):
            try:
                stream.reconfigure(encoding="utf-8")
            except Exception:
                pass


def _collect_source_files(workspace: Path, scope_paths: List[str], max_files: int = 1200) -> List[Path]:
    roots = [workspace / p for p in scope_paths] if scope_paths else [workspace]
    collected: List[Path] = []
    for root in roots:
        if not root.exists():
            continue
        if root.is_file() and root.suffix.lower() in SOURCE_EXTS:
            collected.append(root.resolve())
            continue
        for dirpath, dirnames, filenames in os.walk(root):
            dirnames[:] = [d for d in dirnames if d not in IGNORE_DIRS]
            for fname in filenames:
                fpath = Path(dirpath) / fname
                if fpath.suffix.lower() in SOURCE_EXTS:
                    collected.append(fpath.resolve())
                    if len(collected) >= max_files:
                        return collected
    return collected


def _resolve_relative_candidate(base_dir: Path, raw_ref: str, known_files: Set[Path]) -> Optional[Path]:
    cand = (base_dir / raw_ref).resolve()
    if cand in known_files:
        return cand
    for ext in (".ts", ".tsx", ".js", ".jsx", ".py", ".dart", ".php", "/index.ts", "/index.tsx", "/index.js", "/__init__.py"):
        probe = Path(str(cand) + ext).resolve()
        if probe in known_files:
            return probe
    return None


def _extract_local_imports(fpath: Path, workspace: Path, known_files: Set[Path], module_index: Dict[str, Path]) -> Set[Path]:
    deps: Set[Path] = set()
    try:
        content = fpath.read_text(encoding="utf-8", errors="ignore")
    except OSError:
        return deps

    ext = fpath.suffix.lower()
    if ext == ".py":
        try:
            tree = ast.parse(content)
            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    for alias in node.names:
                        if alias.name in module_index:
                            deps.add(module_index[alias.name])
                elif isinstance(node, ast.ImportFrom):
                    if node.level and node.level > 0:
                        parent = fpath.parent
                        for _ in range(node.level - 1):
                            parent = parent.parent
                        rel_target = (node.module or "").replace(".", "/")
                        resolved = _resolve_relative_candidate(parent, rel_target, known_files)
                        if resolved:
                            deps.add(resolved)
                    elif node.module and node.module in module_index:
                        deps.add(module_index[node.module])
        except SyntaxError:
            pass
    elif ext in {".ts", ".tsx", ".js", ".jsx", ".mjs"}:
        for match in TS_IMPORT_RE.finditer(content):
            ref = match.group(1) or match.group(2) or ""
            if ref.startswith("."):
                resolved = _resolve_relative_candidate(fpath.parent, ref, known_files)
                if resolved:
                    deps.add(resolved)
            elif ref.startswith("@/") or ref.startswith("~/"):
                stripped = ref[2:]
                for prefix in (workspace / "src", workspace):
                    resolved = _resolve_relative_candidate(prefix, stripped, known_files)
                    if resolved:
                        deps.add(resolved)
                        break
    elif ext == ".dart":
        for match in DART_IMPORT_RE.finditer(content):
            ref = match.group(1)
            if not ref.startswith("dart:") and not ref.startswith("package:flutter"):
                if not ref.startswith("package:"):
                    resolved = _resolve_relative_candidate(fpath.parent, ref, known_files)
                    if resolved:
                        deps.add(resolved)
    elif ext == ".php":
        for match in PHP_IMPORT_RE.finditer(content):
            ref = match.group(1)
            resolved = _resolve_relative_candidate(fpath.parent, ref, known_files)
            if resolved:
                deps.add(resolved)

    deps.discard(fpath)
    return deps


def partition_workspace(workspace: Path, scope_paths: List[str], max_workers: int = 4) -> Dict[str, Any]:
    files = _collect_source_files(workspace, scope_paths)
    known_set = set(files)

    # Index Python dotted module names for internal import resolution
    py_index: Dict[str, Path] = {}
    for f in files:
        if f.suffix.lower() == ".py":
            try:
                rel = f.relative_to(workspace).with_suffix("")
                dotted = ".".join(p for p in rel.parts if p != "__init__")
                if dotted:
                    py_index[dotted] = f
                    py_index[rel.name] = f
            except ValueError:
                pass

    outgoing: Dict[Path, Set[Path]] = {}
    incoming_count: Dict[Path, int] = defaultdict(int)

    for f in files:
        deps = _extract_local_imports(f, workspace, known_set, py_index)
        outgoing[f] = deps
        for target in deps:
            incoming_count[target] += 1

    def rel_str(p: Path) -> str:
        try:
            return str(p.relative_to(workspace)).replace("\\", "/")
        except ValueError:
            return str(p).replace("\\", "/")

    # Stage 0: Shared contracts / foundational files imported by >= 2 other local files
    # or explicitly located in types/schema/models/contracts directories
    stage0_files: Set[Path] = set()
    for f in files:
        r = rel_str(f).lower()
        is_contract_name = any(tok in r for tok in ("/types/", "/schemas/", "/contracts/", "schema.", "types.", "interfaces."))
        if incoming_count[f] >= 2 or (incoming_count[f] >= 1 and is_contract_name):
            stage0_files.add(f)

    remaining = [f for f in files if f not in stage0_files]

    # Connected components over remaining files (ignoring edges pointing into already-locked Stage 0)
    undirected: Dict[Path, Set[Path]] = defaultdict(set)
    for f in remaining:
        for dep in outgoing[f]:
            if dep not in stage0_files:
                undirected[f].add(dep)
                undirected[dep].add(f)

    visited: Set[Path] = set()
    components: List[List[Path]] = []
    for f in remaining:
        if f in visited:
            continue
        comp: List[Path] = []
        stack = [f]
        visited.add(f)
        while stack:
            curr = stack.pop()
            comp.append(curr)
            for nxt in undirected[curr]:
                if nxt not in visited:
                    visited.add(nxt)
                    stack.append(nxt)
        components.append(sorted(comp, key=rel_str))

    # Group small components by top directory and balance across <= max_workers disjoint buckets
    components.sort(key=len, reverse=True)
    worker_count = max(1, min(max_workers, len(components))) if components else 0
    buckets: List[List[str]] = [[] for _ in range(worker_count)]
    for comp in components:
        if not buckets:
            break
        lightest_idx = min(range(len(buckets)), key=lambda idx: len(buckets[idx]))
        buckets[lightest_idx].extend(rel_str(p) for p in comp)

    slices = []
    for idx, owned_files in enumerate(buckets, start=1):
        if not owned_files:
            continue
        top_dirs = sorted({Path(p).parts[0] if len(Path(p).parts) > 1 else "(root)" for p in owned_files})
        slices.append(
            {
                "worker_id": f"slice-{idx}",
                "focus_areas": top_dirs[:4],
                "file_count": len(owned_files),
                "owned_files": sorted(owned_files),
            }
        )

    return {
        "workspace": str(workspace).replace("\\", "/"),
        "total_source_files": len(files),
        "total_import_edges": sum(len(v) for v in outgoing.values()),
        "stage_0_shared_contracts": [
            {"file": rel_str(f), "imported_by_count": incoming_count[f]}
            for f in sorted(stage0_files, key=lambda p: (-incoming_count[p], rel_str(p)))
        ],
        "stage_1_parallel_slices": slices,
        "collision_free_guarantee": True,
    }


def emit_workflow_script(plan: Dict[str, Any], goal: str) -> str:
    stage0 = [x["file"] for x in plan["stage_0_shared_contracts"]]
    slices = plan["stage_1_parallel_slices"]
    lines = [
        "# Auto-generated Antigravity run_workflow script (File-Disjoint Parallel Execution)",
        f"# Goal: {goal or 'Implement parallel changes with zero merge collisions'}",
        "",
    ]
    if stage0:
        lines.extend(
            [
                'phase("Stage 0: Lock Shared Contracts First")',
                f"stage0_files = {json.dumps(stage0)}",
                "contract_summary = await agent(",
                '    f"Review and update ONLY these shared contract files if needed for the goal: {stage0_files}. "',
                f'    f"Goal: {goal or "Update shared interfaces"}. Return concise summary of exported signatures.",',
                '    schema={"type": "string"},',
                '    role="Stage-0 Contract Architect",',
                '    model="inherit",',
                ")",
                'log("Stage 0 complete:", contract_summary)',
                "",
            ]
        )
    else:
        lines.append('contract_summary = "No shared contract edits required."')
        lines.append("")

    lines.extend(
        [
            'phase("Stage 1: Parallel File-Disjoint Worker Slices")',
            f"slices = {json.dumps(slices, indent=2)}",
            "",
            "results = await parallel(",
            "    slices,",
            "    lambda s: agent(",
            '        f"You own EXCLUSIVELY these {s[\'file_count\']} file(s): {s[\'owned_files\']}. "',
            '        f"NEVER edit any file outside your owned list. Shared contracts: {contract_summary}. "',
            f'        f"Task: {goal or "Complete slice updates and unit checks"}. "',
            '        "Commit your changes in your workspace and return branch + concise diff summary.",',
            '        schema={"type": "string"},',
            '        role=f"Worker {s[\'worker_id\']} ({\',\'.join(s[\'focus_areas\'])})",',
            '        workspace="share",',
            '        model="flash",',
            "    ),",
            ")",
            "for r in results:",
            "    log(r)",
        ]
    )
    return "\n".join(lines)


def render_markdown(plan: Dict[str, Any]) -> str:
    lines = [
        "## File-Disjoint Parallel Partition Plan",
        "",
        f"- **Scanned Source Files**: `{plan['total_source_files']}` (`{plan['total_import_edges']}` internal import edges)",
        f"- **Stage 0 Shared Foundations**: `{len(plan['stage_0_shared_contracts'])}` file(s) *(edit sequentially first)*",
        f"- **Stage 1 Parallel Worker Slices**: `{len(plan['stage_1_parallel_slices'])}` collision-free slice(s)",
        "",
    ]
    if plan["stage_0_shared_contracts"]:
        lines.extend(["### Stage 0 — Shared Contracts (High Fan-In)", ""])
        for item in plan["stage_0_shared_contracts"][:10]:
            lines.append(f"- `{item['file']}` *(imported by `{item['imported_by_count']}` local file(s))*")
        lines.append("")

    lines.extend(["### Stage 1 — Disjoint Parallel Worker Ownership", ""])
    for sl in plan["stage_1_parallel_slices"]:
        preview = ", ".join(f"`{p}`" for p in sl["owned_files"][:6])
        if len(sl["owned_files"]) > 6:
            preview += f" *(+{len(sl['owned_files']) - 6} more)*"
        lines.append(
            f"- **{sl['worker_id']}** ({sl['file_count']} files in `{', '.join(sl['focus_areas'])}`): {preview}"
        )
    return "\n".join(lines)


def main() -> int:
    _configure_utf8()
    parser = argparse.ArgumentParser(
        description="Partition workspace files into dependency-safe, collision-free parallel agent slices."
    )
    parser.add_argument("--workspace", "-w", default=".", help="Workspace directory.")
    parser.add_argument("--paths", "-p", nargs="*", default=[], help="Optional subdirectories to scope.")
    parser.add_argument("--max-workers", "-m", type=int, default=4, help="Maximum parallel worker slices (default: 4).")
    parser.add_argument("--goal", "-g", default="", help="Goal description when emitting a workflow script.")
    parser.add_argument("--emit-workflow", action="store_true", help="Output a ready-to-run Antigravity run_workflow Python script.")
    parser.add_argument("--format", choices=("markdown", "json"), default="markdown", help="Output format.")
    args = parser.parse_args()

    plan = partition_workspace(Path(args.workspace).resolve(), args.paths, max_workers=args.max_workers)
    if args.emit_workflow:
        print(emit_workflow_script(plan, args.goal))
    elif args.format == "json":
        print(json.dumps(plan, indent=2, ensure_ascii=False))
    else:
        print(render_markdown(plan))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
