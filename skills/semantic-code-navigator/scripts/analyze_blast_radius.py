#!/usr/bin/env python3
"""Transitive Reverse-Import Blast-Radius & Minimal Test Selector.

Given one or more modified/target files, walks the workspace's reverse import
graph (`who imports X -> who imports Y`) to identify:
  1. Direct Dependents (depth = 1)
  2. Transitive Downstream Dependents (depth >= 2)
  3. Affected Test Files ONLY (so the agent runs 2 targeted tests in 1s instead
     of the entire 500-test monorepo suite!)

Zero external dependencies (Python 3.8+ stdlib only).
"""

from __future__ import annotations

import argparse
import importlib.util
import json
import sys
from collections import defaultdict, deque
from pathlib import Path
from typing import Any, Dict, List, Set


def _configure_utf8() -> None:
    for stream in (sys.stdout, sys.stderr):
        if hasattr(stream, "reconfigure"):
            try:
                stream.reconfigure(encoding="utf-8")
            except Exception:
                pass


def _load_slice_module():
    slice_script = Path(__file__).resolve().parents[2] / "parallel-slice-architect" / "scripts" / "partition_parallel_slices.py"
    spec = importlib.util.spec_from_file_location("partition_parallel_slices", slice_script)
    assert spec and spec.loader
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def _is_test_file(rel_path: str) -> bool:
    lower = rel_path.lower()
    name = Path(lower).name
    return (
        "/test/" in f"/{lower}"
        or "/tests/" in f"/{lower}"
        or "/__tests__/" in f"/{lower}"
        or name.startswith("test_")
        or name.endswith(("_test.py", "_test.dart", "_test.go", ".test.ts", ".test.tsx", ".spec.ts", ".spec.tsx", ".test.js", ".spec.js"))
    )


def compute_blast_radius(workspace: Path, target_files: List[str]) -> Dict[str, Any]:
    slice_mod = _load_slice_module()
    files: List[Path] = slice_mod._collect_source_files(workspace, [])
    known_set: Set[Path] = set(files)

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

    reverse_graph: Dict[Path, Set[Path]] = defaultdict(set)
    for f in files:
        deps = slice_mod._extract_local_imports(f, workspace, known_set, py_index)
        for dep in deps:
            reverse_graph[dep].add(f)

    def rel_str(p: Path) -> str:
        try:
            return str(p.relative_to(workspace)).replace("\\", "/")
        except ValueError:
            return str(p).replace("\\", "/")

    seed_paths: List[Path] = []
    for raw_t in target_files:
        cand = (workspace / raw_t).resolve()
        if cand in known_set:
            seed_paths.append(cand)
        else:
            # Fuzzy suffix match
            norm_t = raw_t.replace("\\", "/").lower()
            for kf in files:
                if rel_str(kf).lower().endswith(norm_t):
                    seed_paths.append(kf)

    direct_deps: Set[Path] = set()
    transitive_deps: Set[Path] = set()
    visited: Set[Path] = set(seed_paths)
    queue: deque[tuple[Path, int]] = deque((sp, 0) for sp in seed_paths)

    while queue:
        curr, depth = queue.popleft()
        for importer in reverse_graph.get(curr, set()):
            if importer not in visited:
                visited.add(importer)
                if depth == 0:
                    direct_deps.add(importer)
                else:
                    transitive_deps.add(importer)
                queue.append((importer, depth + 1))

    all_impacted = seed_paths + sorted(direct_deps | transitive_deps)
    affected_tests: Set[str] = {rel_str(p) for p in all_impacted if _is_test_file(rel_str(p))}

    # Heuristic fallback: also match test files sharing stem with seed files
    seed_stems = {p.stem.lower() for p in seed_paths}
    for f in files:
        rf = rel_str(f)
        if _is_test_file(rf) and any(st in f.stem.lower() for st in seed_stems):
            affected_tests.add(rf)

    total_files = max(1, len(files))
    impacted_count = len(direct_deps) + len(transitive_deps)
    scope_reduction_pct = max(0.0, round((1.0 - (len(seed_paths) + impacted_count) / total_files) * 100, 1))

    return {
        "targets": [rel_str(p) for p in seed_paths],
        "total_workspace_files": len(files),
        "direct_dependents": sorted(rel_str(p) for p in direct_deps),
        "transitive_dependents": sorted(rel_str(p) for p in transitive_deps),
        "affected_test_files": sorted(affected_tests),
        "inspection_scope_reduction_pct": scope_reduction_pct,
    }


def render_markdown(rep: Dict[str, Any]) -> str:
    lines = [
        "## Reverse-Import Blast Radius & Minimal Test Plan",
        f"- **Modified / Target File(s)**: {', '.join(f'`{t}`' for t in rep['targets']) or '_(none matched)_'}",
        f"- **Direct Dependents (`depth=1`)**: `{len(rep['direct_dependents'])}` file(s)",
        f"- **Transitive Dependents (`depth>=2`)**: `{len(rep['transitive_dependents'])}` file(s)",
        f"- **Scope Narrowing**: **{rep['inspection_scope_reduction_pct']}% of workspace safely skipped**",
    ]
    if rep["direct_dependents"]:
        lines.extend(["", "### Direct Importers (Verify Signatures Here)", ""])
        for d in rep["direct_dependents"][:15]:
            lines.append(f"- `{d}`")
    if rep["transitive_dependents"]:
        lines.extend(["", "### Transitive Downstream Files", ""])
        for t in rep["transitive_dependents"][:12]:
            lines.append(f"- `{t}`")
    lines.extend(["", "### Minimal Affected Test Suite to Run", ""])
    if rep["affected_test_files"]:
        for tf in rep["affected_test_files"]:
            lines.append(f"- `{tf}`")
    else:
        lines.append("- _No dedicated unit test file imports these targets yet._")
    return "\n".join(lines)


def main() -> int:
    _configure_utf8()
    parser = argparse.ArgumentParser(description="Trace reverse-import blast radius and select minimal affected tests.")
    parser.add_argument("targets", nargs="+", help="One or more relative file paths (or filename suffixes) being modified.")
    parser.add_argument("--workspace", "-w", default=".", help="Workspace root directory.")
    parser.add_argument("--format", choices=("markdown", "json"), default="markdown", help="Output format.")
    args = parser.parse_args()

    rep = compute_blast_radius(Path(args.workspace).resolve(), args.targets)
    if args.format == "json":
        print(json.dumps(rep, indent=2, ensure_ascii=False))
    else:
        print(render_markdown(rep))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
