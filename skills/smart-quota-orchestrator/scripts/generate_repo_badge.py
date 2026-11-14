#!/usr/bin/env python3
"""Dynamic Repository Token-Efficiency Shield Badge Generator (`sqo badge`).

Runs empirical compression + prompt-tax benchmarks on a workspace and generates a crisp
GitHub-ready SVG badge (`sqo-badge.svg`) plus Markdown embed snippet linking back to
https://sqo.elnemer-ai.com so teams can showcase verified AI readiness!
"""

from __future__ import annotations

import argparse
import importlib.util
import sys
from pathlib import Path

SKILLS_ROOT = Path(__file__).resolve().parents[2]


def _load_mod(rel_path: str):
    target = SKILLS_ROOT / rel_path
    spec = importlib.util.spec_from_file_location(rel_path.replace("/", "_"), target)
    assert spec and spec.loader
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def build_badge_svg(workspace: Path) -> tuple[str, dict]:
    bench_mod = _load_mod("smart-quota-orchestrator/scripts/benchmark_suite.py")
    tax_mod = _load_mod("prompt-tax-profiler/scripts/optimize_prompt_rules.py")

    bench = bench_mod.run_live_benchmark(workspace, SKILLS_ROOT)
    tax = tax_mod.profile_workspace(workspace)
    pct = bench["average_token_reduction_pct"]
    grade = tax["grade"].split(" ")[0]

    label = "Smart Quota OS"
    val = f"-{pct}% Tokens | Grade {grade}"
    svg = f"""<svg xmlns="http://www.w3.org/2000/svg" width="276" height="28" role="img" aria-label="{label}: {val}">
  <defs>
    <linearGradient id="l" x1="0" y1="0" x2="1" y2="0"><stop offset="0%" stop-color="#0f172a"/><stop offset="100%" stop-color="#1e293b"/></linearGradient>
    <linearGradient id="r" x1="0" y1="0" x2="1" y2="0"><stop offset="0%" stop-color="#0284c7"/><stop offset="100%" stop-color="#10b981"/></linearGradient>
  </defs>
  <rect width="118" height="28" rx="6" fill="url(#l)"/>
  <rect x="114" width="162" height="28" rx="6" fill="url(#r)"/>
  <rect x="114" width="6" height="28" fill="url(#r)"/>
  <g fill="#fff" font-family="Segoe UI, Inter, DejaVu Sans, sans-serif" font-size="11.5" font-weight="700">
    <text x="59" y="18" text-anchor="middle" fill="#38bdf8">⚡ {label}</text>
    <text x="196" y="18" text-anchor="middle">{val}</text>
  </g>
</svg>
"""
    return svg, {"reduction_pct": pct, "grade": grade}


def main() -> int:
    for s in (sys.stdout, sys.stderr):
        if hasattr(s, "reconfigure"):
            try:
                s.reconfigure(encoding="utf-8")
            except Exception:
                pass

    parser = argparse.ArgumentParser(description="Generate a verified Smart Quota OS SVG shield badge for any repo.")
    parser.add_argument("--workspace", "-w", default=".", help="Workspace path.")
    parser.add_argument("--output", "-o", default="sqo-badge.svg", help="Output SVG path.")
    args = parser.parse_args()

    ws = Path(args.workspace).resolve()
    svg, meta = build_badge_svg(ws)
    out = Path(args.output)
    out.write_text(svg, encoding="utf-8")
    print(f"[OK] Generated SVG badge ({meta['reduction_pct']}% reduction, Grade {meta['grade']}): {out}")
    print('Embed in README.md: [![Protected by Smart Quota OS](https://sqo.elnemer-ai.com/badge.svg)](https://sqo.elnemer-ai.com)')
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
