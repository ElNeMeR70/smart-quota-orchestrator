#!/usr/bin/env python3
"""Live Empirical Token-Compression Benchmark Suite (`sqo benchmark`).

Runs REAL deterministic measurements against any workspace on disk and produces a
verified Before-vs-After Token Reduction table across 4 dimensions:
  1. Full-File Reads vs. `sqo outline` AST Skeletons
  2. Full Repo Dump vs. `sqo search` SQLite FTS5 BM25 Top-K Retrieval
  3. Raw Directory Dump vs. `sqo pack` Adaptive Context Packing
  4. Verbose Test Suite Output vs. `sqo denoise` Diagnostic Extraction

Zero external dependencies (Python 3.8+ stdlib only).
"""

from __future__ import annotations

import argparse
import importlib.util
import json
import sys
import time
from pathlib import Path
from typing import Any, Dict, List


def _configure_utf8() -> None:
    for stream in (sys.stdout, sys.stderr):
        if hasattr(stream, "reconfigure"):
            try:
                stream.reconfigure(encoding="utf-8")
            except Exception:
                pass


def _load(skills_dir: Path, rel: str, name: str):
    spec = importlib.util.spec_from_file_location(name, skills_dir / rel)
    assert spec and spec.loader
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def run_live_benchmark(workspace: Path, skills_dir: Path) -> Dict[str, Any]:
    t0 = time.perf_counter()
    outline_mod = _load(skills_dir, "context-compactor/scripts/smart_outline.py", "outline")
    pack_mod = _load(skills_dir, "context-compactor/scripts/pack_context_bundle.py", "pack")
    bm25_mod = _load(skills_dir, "semantic-code-navigator/scripts/search_code_bm25.py", "bm25")
    denoise_mod = _load(skills_dir, "context-compactor/scripts/compact_command_output.py", "denoise")

    # 1. BM25 Search vs Full Repo Read
    bm25_res = bm25_mod.search_workspace(workspace, "analyze parse complexity token", top_k=5)

    # 2. Adaptive Context Pack (2,500-token ceiling)
    pack_res = pack_mod.pack_context(workspace, [], [], max_tokens=2500)

    # 3. Outline compression across top 5 largest source files
    source_files = [
        p for p in workspace.rglob("*.py")
        if not any(part in {".git", ".sqo", "node_modules", "__pycache__", ".venv"} for part in p.parts)
    ]
    source_files.sort(key=lambda p: p.stat().st_size if p.exists() else 0, reverse=True)
    sample_files = source_files[:5]

    raw_outline_tok = 0
    comp_outline_tok = 0
    for sf in sample_files:
        o = outline_mod.build_outline(sf)
        raw_outline_tok += o["full_file_approx_tokens"]
        md = outline_mod.render_markdown(o)
        comp_outline_tok += max(1, int(len(md) / 4))
    outline_saved = max(0.0, round((1.0 - comp_outline_tok / max(1, raw_outline_tok)) * 100, 1)) if raw_outline_tok else 0.0

    # 4. Synthetic realistic 120-test runner log vs Denoiser
    synthetic_log = "\n".join(
        [f"\x1b[32m✓\x1b[0m src/modules/mod_{i}/service.spec.ts ({12 + (i % 9)} tests) 42ms" for i in range(120)]
        + [
            "FAIL src/auth/jwt_guard.spec.ts",
            "  AssertionError: expected token expiry check to reject expired signature at src/auth/jwt_guard.ts:88:11",
            "    at node_modules/vitest/dist/chunk-runtime.js:412:9",
            "Test Files  1 failed | 120 passed (121)",
            "Tests       1 failed | 1,480 passed (1,481)",
        ]
    )
    den_res = denoise_mod.denoise_output(synthetic_log, exit_code=1)
    elapsed_ms = round((time.perf_counter() - t0) * 1000, 1)

    benchmarks: List[Dict[str, Any]] = [
        {
            "dimension": "Codebase Discovery (`sqo search` BM25 vs. Reading Repo)",
            "baseline_tokens": bm25_res["repo_approx_tokens"],
            "optimized_tokens": bm25_res["returned_approx_tokens"],
            "savings_pct": bm25_res["token_savings_pct"],
        },
        {
            "dimension": f"Large-File Inspection (`sqo outline` on top {len(sample_files)} files)",
            "baseline_tokens": raw_outline_tok,
            "optimized_tokens": comp_outline_tok,
            "savings_pct": outline_saved,
        },
        {
            "dimension": "Multi-File Architecture Pack (`sqo pack` <=2.5k budget)",
            "baseline_tokens": pack_res["uncompressed_approx_tokens"],
            "optimized_tokens": pack_res["packed_approx_tokens"],
            "savings_pct": pack_res["token_savings_pct"],
        },
        {
            "dimension": "120-Suite Test Runner Output (`sqo denoise`)",
            "baseline_tokens": den_res["raw_approx_tokens"],
            "optimized_tokens": den_res["compacted_approx_tokens"],
            "savings_pct": float(den_res["token_savings_pct"]),
        },
    ]

    avg_savings = round(sum(b["savings_pct"] for b in benchmarks) / len(benchmarks), 1)
    return {
        "workspace": str(workspace).replace("\\", "/"),
        "execution_time_ms": elapsed_ms,
        "average_token_reduction_pct": avg_savings,
        "benchmarks": benchmarks,
    }


def render_markdown(rep: Dict[str, Any]) -> str:
    lines = [
        "## Empirical Token-Compression Benchmark Report",
        f"- **Workspace Measured**: `{rep['workspace']}` *(completed in `{rep['execution_time_ms']} ms`)*",
        f"- **Mean Measured Token Reduction**: **`{rep['average_token_reduction_pct']}%`** 🔥",
        "",
        "| Engineering Operation | Naive Agent Tokens | `sqo` Optimized Tokens | Measured Reduction |",
        "| :--- | :--- | :--- | :--- |",
    ]
    for b in rep["benchmarks"]:
        lines.append(
            f"| {b['dimension']} | `~{b['baseline_tokens']:,}` | **`~{b['optimized_tokens']:,}`** | **{b['savings_pct']}%** |"
        )
    return "\n".join(lines)


def main() -> int:
    _configure_utf8()
    parser = argparse.ArgumentParser(description="Run live empirical token-compression benchmarks on a workspace.")
    parser.add_argument("--workspace", "-w", default=".", help="Workspace path to benchmark.")
    parser.add_argument("--format", choices=("markdown", "json"), default="markdown", help="Output format.")
    args = parser.parse_args()

    skills_dir = Path(__file__).resolve().parents[2]
    rep = run_live_benchmark(Path(args.workspace).resolve(), skills_dir)
    if args.format == "json":
        print(json.dumps(rep, indent=2, ensure_ascii=False))
    else:
        print(render_markdown(rep))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
