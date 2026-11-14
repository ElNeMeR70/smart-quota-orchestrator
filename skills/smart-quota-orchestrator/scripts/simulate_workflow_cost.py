#!/usr/bin/env python3
"""Quadratic Monolith vs. Multi-Agent Workflow Quota & Token Simulator.

Demonstrates and quantifies why reading N files sequentially inside a single
frontier model session triggers O(T^2) cumulative context billing, whereas
Orchestrator delegation or `run_workflow(model='flash')` keeps billing linear!

Zero external dependencies (Python 3.8+ stdlib only).
"""

from __future__ import annotations

import argparse
import json
import sys
from typing import Any, Dict, List

# Relative quota-weight multipliers normalized to Hydrogen/Flash-Lite = 1.0x
MODEL_WEIGHTS: Dict[str, Dict[str, float]] = {
    "carbon_high_monolith": {"label": "Standalone Carbon (High) — Monolithic", "input_w": 4.0, "think_tok": 3200, "think_w": 6.0},
    "carbon_medium_monolith": {"label": "Standalone Carbon (Medium) — Monolithic", "input_w": 4.0, "think_tok": 1400, "think_w": 5.0},
    "orchestrator_carbon": {"label": "Orchestrator (Carbon + Hydrogen Workers)", "input_w": 1.65, "think_tok": 650, "think_w": 2.2},
    "orchestrator_argon": {"label": "Orchestrator (Argon + Hydrogen Workers)", "input_w": 1.25, "think_tok": 450, "think_w": 1.5},
    "workflow_flash_fanout": {"label": "Planner + Parallel run_workflow (flash)", "input_w": 1.0, "think_tok": 300, "think_w": 1.1},
}


def _configure_utf8() -> None:
    for stream in (sys.stdout, sys.stderr):
        if hasattr(stream, "reconfigure"):
            try:
                stream.reconfigure(encoding="utf-8")
            except Exception:
                pass


def simulate(files: int, avg_loc: int, turns: int, base_system_tokens: int = 3500) -> Dict[str, Any]:
    tokens_per_file = max(80, avg_loc * 9)  # ~9 tokens per line of code
    total_repo_slice_tokens = files * tokens_per_file

    strategies: List[Dict[str, Any]] = []

    for key, cfg in MODEL_WEIGHTS.items():
        if key.endswith("_monolith"):
            # Every turn accumulates more read files & tool outputs in the single shared history!
            delta_per_turn = int(total_repo_slice_tokens / max(1, turns)) + 450
            cumulative_input = sum(base_system_tokens + (step * delta_per_turn) for step in range(1, turns + 1))
            thinking_total = turns * int(cfg["think_tok"])
        elif key.startswith("orchestrator_"):
            # Planner runs 25% of turns; Hydrogen executes 75% with targeted reads
            effective_turns = max(3, int(turns * 0.8))
            delta_per_turn = int((total_repo_slice_tokens * 0.55) / max(1, effective_turns)) + 300
            cumulative_input = sum(base_system_tokens + (step * delta_per_turn) for step in range(1, effective_turns + 1))
            thinking_total = effective_turns * int(cfg["think_tok"])
        else:
            # Parallel fan-out: 2 planner turns + N isolated single-file worker turns (no quadratic history!)
            planner_input = 2 * (base_system_tokens + 1200) + (files * 120)
            worker_input = files * (1800 + tokens_per_file)
            cumulative_input = planner_input + worker_input
            thinking_total = (2 * 1200) + (files * int(cfg["think_tok"]))

        weighted_units = int((cumulative_input * cfg["input_w"] + thinking_total * cfg["think_w"]) / 1000)
        strategies.append({
            "id": key,
            "strategy": cfg["label"],
            "cumulative_input_tokens": cumulative_input,
            "total_thinking_tokens": thinking_total,
            "relative_quota_units": max(1, weighted_units),
        })

    baseline_units = strategies[0]["relative_quota_units"]
    for s in strategies:
        saved = round((1.0 - (s["relative_quota_units"] / max(1, baseline_units))) * 100, 1)
        s["quota_savings_vs_carbon_high_pct"] = max(0.0, saved)

    best = min(strategies, key=lambda x: x["relative_quota_units"])
    return {
        "parameters": {"files": files, "avg_loc": avg_loc, "turns": turns},
        "strategies": strategies,
        "recommended_winner": best["strategy"],
    }


def render_markdown(sim: Dict[str, Any]) -> str:
    p = sim["parameters"]
    lines = [
        f"## Quota Burn Simulation (`{p['files']}` files × `{p['avg_loc']}` LOC over `{p['turns']}` turns)",
        "",
        "| Execution Strategy | Cumulative Input Tokens | Thinking Tokens | Relative Quota Cost | Quota Saved |",
        "| :--- | :--- | :--- | :--- | :--- |",
    ]
    for s in sim["strategies"]:
        saved = f"**{s['quota_savings_vs_carbon_high_pct']}%**" if s["quota_savings_vs_carbon_high_pct"] > 0 else "Baseline (0%)"
        lines.append(
            f"| {s['strategy']} | `{s['cumulative_input_tokens']:,}` | `{s['total_thinking_tokens']:,}` | `{s['relative_quota_units']:,} units` | {saved} |"
        )
    lines.append(f"\n> **Lowest-Burn Strategy:** `{sim['recommended_winner']}`")
    return "\n".join(lines)


def main() -> int:
    _configure_utf8()
    parser = argparse.ArgumentParser(description="Simulate token & quota burn across monolithic vs multi-agent execution modes.")
    parser.add_argument("--files", "-f", type=int, default=12, help="Number of files touched/inspected (default: 12).")
    parser.add_argument("--avg-loc", "-l", type=int, default=220, help="Average lines of code per file (default: 220).")
    parser.add_argument("--turns", "-t", type=int, default=16, help="Conversation/tool turns (default: 16).")
    parser.add_argument("--format", choices=("markdown", "json"), default="markdown", help="Output format.")
    args = parser.parse_args()

    res = simulate(max(1, args.files), max(10, args.avg_loc), max(2, args.turns))
    if args.format == "json":
        print(json.dumps(res, indent=2, ensure_ascii=False))
    else:
        print(render_markdown(res))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
