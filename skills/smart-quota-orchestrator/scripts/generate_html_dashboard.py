#!/usr/bin/env python3
"""Generate a self-contained Interactive HTML Quota & Context Engineering Dashboard.

Aggregates:
  1. Workspace Complexity & Parallelizability metrics
  2. File-Disjoint Parallel Worker Slice Plan
  3. Prompt & Skill Token-Tax Profile
  4. Context-Bomb Ignore Scan
  5. Optional Live Quota Pool JSON & Session Burn Audit

Outputs a single sleek dark-glassmorphism `.html` report with zero external CDN dependencies!
"""

from __future__ import annotations

import argparse
import datetime as dt
import html
import importlib.util
import json
import sys
from pathlib import Path
from typing import Any, Dict, Optional


def _configure_utf8() -> None:
    for stream in (sys.stdout, sys.stderr):
        if hasattr(stream, "reconfigure"):
            try:
                stream.reconfigure(encoding="utf-8")
            except Exception:
                pass


def _load_sibling(repo_skills_dir: Path, rel_path: str, name: str):
    target = repo_skills_dir / rel_path
    spec = importlib.util.spec_from_file_location(name, target)
    assert spec and spec.loader
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def build_dashboard_html(
    workspace: Path,
    skills_root: Path,
    quota_json_path: Optional[Path] = None,
    task_desc: str = "Full-stack feature implementation & verification",
) -> str:
    comp_mod = _load_sibling(skills_root, "smart-quota-orchestrator/scripts/analyze_task_complexity.py", "comp")
    sim_mod = _load_sibling(skills_root, "smart-quota-orchestrator/scripts/simulate_workflow_cost.py", "sim")
    slice_mod = _load_sibling(skills_root, "parallel-slice-architect/scripts/partition_parallel_slices.py", "slc")
    tax_mod = _load_sibling(skills_root, "prompt-tax-profiler/scripts/optimize_prompt_rules.py", "tax")
    ign_mod = _load_sibling(skills_root, "context-compactor/scripts/generate_agent_ignore.py", "ign")

    comp = comp_mod.evaluate_task(workspace, task_desc, [])
    files_n = max(4, comp["workspace_metrics"]["total_code_files"])
    avg_loc = max(40, int(comp["workspace_metrics"]["total_loc"] / max(1, files_n)))
    sim = sim_mod.simulate(files=min(files_n, 25), avg_loc=avg_loc, turns=16)
    slices = slice_mod.partition_workspace(workspace, [], max_workers=4)
    tax = tax_mod.profile_workspace(workspace)
    bombs = ign_mod.scan_token_bombs(workspace)

    pools_html = ""
    if quota_json_path and quota_json_path.is_file():
        pool_mod = _load_sibling(skills_root, "smart-quota-orchestrator/scripts/parse_quota_pools.py", "pool")
        pool_data = pool_mod.analyze_pools(json.loads(quota_json_path.read_text(encoding="utf-8")))
        rows = []
        for p in pool_data["pools"]:
            pct = p["quota_pct"] or 0
            badge_cls = "ok" if p["health"] == "HEALTHY" else ("warn" if p["health"] == "CONSERVE" else "crit")
            rows.append(
                f"<tr><td><strong>{html.escape(p['pool_name'])}</strong></td>"
                f"<td><div class='bar'><span style='width:{min(100, pct)}%'></span></div> {html.escape(p['quota_remaining'])}</td>"
                f"<td><span class='pill {badge_cls}'>{html.escape(p['health'])}</span></td>"
                f"<td>{html.escape(p['time_until_reset'])}</td></tr>"
            )
        pools_html = f"""
        <section class="card full">
          <h2>Live Model Quota Pools</h2>
          <table>
            <thead><tr><th>Quota Pool</th><th>Remaining</th><th>Status</th><th>Resets In</th></tr></thead>
            <tbody>{''.join(rows)}</tbody>
          </table>
        </section>
        """

    sim_rows = []
    for s in sim["strategies"]:
        sim_rows.append(
            f"<tr><td>{html.escape(s['strategy'])}</td>"
            f"<td>{s['cumulative_input_tokens']:,}</td>"
            f"<td>{s['total_thinking_tokens']:,}</td>"
            f"<td><strong>{s['quota_savings_vs_carbon_high_pct']}%</strong></td></tr>"
        )

    slice_items = []
    for sl in slices["stage_1_parallel_slices"]:
        owned = ", ".join(sl["owned_files"][:5])
        if len(sl["owned_files"]) > 5:
            owned += f" (+{len(sl['owned_files']) - 5} more)"
        slice_items.append(
            f"<li><strong>{html.escape(sl['worker_id'])}</strong> ({sl['file_count']} files): <code>{html.escape(owned)}</code></li>"
        )

    generated_ts = dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    ws_name = html.escape(workspace.name)

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>Smart Quota &amp; Swarm Orchestrator — {ws_name}</title>
  <style>
    :root {{
      --bg: #090d16;
      --card: rgba(17, 25, 40, 0.86);
      --border: rgba(99, 102, 241, 0.25);
      --text: #e2e8f0;
      --muted: #94a3b8;
      --cyan: #38bdf8;
      --emerald: #34d399;
      --amber: #fbbf24;
      --rose: #fb7185;
    }}
    * {{ box-sizing: border-box; }}
    body {{
      margin: 0;
      padding: 32px 20px;
      font-family: Inter, -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
      background: radial-gradient(circle at top right, #1e1b4b, var(--bg) 55%);
      color: var(--text);
    }}
    .wrap {{ max-width: 1120px; margin: 0 auto; }}
    header {{
      display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap;
      gap: 12px; margin-bottom: 24px; padding-bottom: 16px; border-bottom: 1px solid var(--border);
    }}
    h1 {{ margin: 0; font-size: 1.55rem; background: linear-gradient(90deg, var(--cyan), var(--emerald)); -webkit-background-clip: text; -webkit-text-fill-color: transparent; }}
    .meta {{ color: var(--muted); font-size: 0.88rem; }}
    .grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(240px, 1fr)); gap: 16px; margin-bottom: 20px; }}
    .card {{
      background: var(--card); border: 1px solid var(--border); border-radius: 16px;
      padding: 20px; box-shadow: 0 12px 32px rgba(0, 0, 0, 0.35);
    }}
    .card.full {{ margin-bottom: 20px; }}
    .kpi-label {{ color: var(--muted); font-size: 0.82rem; text-transform: uppercase; letter-spacing: 0.05em; }}
    .kpi-val {{ font-size: 1.85rem; font-weight: 700; margin: 8px 0 4px; color: var(--cyan); }}
    .kpi-sub {{ font-size: 0.84rem; color: var(--emerald); }}
    h2 {{ margin: 0 0 14px; font-size: 1.1rem; color: #f8fafc; }}
    table {{ width: 100%; border-collapse: collapse; font-size: 0.9rem; }}
    th, td {{ text-align: left; padding: 10px 8px; border-bottom: 1px solid rgba(148, 163, 184, 0.14); }}
    th {{ color: var(--muted); font-weight: 600; }}
    code {{ background: rgba(15, 23, 42, 0.9); padding: 2px 6px; border-radius: 6px; color: var(--cyan); font-size: 0.84rem; }}
    .pill {{ padding: 3px 10px; border-radius: 999px; font-size: 0.76rem; font-weight: 700; }}
    .pill.ok {{ background: rgba(52, 211, 153, 0.18); color: var(--emerald); }}
    .pill.warn {{ background: rgba(251, 191, 36, 0.18); color: var(--amber); }}
    .pill.crit {{ background: rgba(251, 113, 133, 0.2); color: var(--rose); }}
    .bar {{ display: inline-block; width: 90px; height: 8px; background: #1e293b; border-radius: 99px; overflow: hidden; vertical-align: middle; margin-right: 6px; }}
    .bar span {{ display: block; height: 100%; background: linear-gradient(90deg, var(--cyan), var(--emerald)); }}
    ul {{ margin: 0; padding-left: 18px; line-height: 1.7; font-size: 0.92rem; }}
  </style>
</head>
<body>
  <div class="wrap">
    <header>
      <div>
        <h1>⚡ Smart Quota &amp; Swarm Orchestrator — Telemetry Center</h1>
        <div class="meta">Workspace: <code>{html.escape(str(workspace))}</code> • Generated: {generated_ts}</div>
      </div>
      <span class="pill ok">{html.escape(tax['grade'])}</span>
    </header>

    <div class="grid">
      <div class="card">
        <div class="kpi-label">Complexity Score</div>
        <div class="kpi-val">{comp['complexity_score']} / 100</div>
        <div class="kpi-sub">Parallelizability: {comp['parallelizability_index']}</div>
      </div>
      <div class="card">
        <div class="kpi-label">Source Footprint</div>
        <div class="kpi-val">{comp['workspace_metrics']['total_code_files']} files</div>
        <div class="kpi-sub">{comp['workspace_metrics']['total_loc']:,} total lines</div>
      </div>
      <div class="card">
        <div class="kpi-label">Static Prompt Tax / Turn</div>
        <div class="kpi-val">~{tax['total_baseline_tokens_per_turn']:,} tok</div>
        <div class="kpi-sub">{len(tax['skills'])} progressive skill(s)</div>
      </div>
      <div class="card">
        <div class="kpi-label">Preventable Bomb Tokens</div>
        <div class="kpi-val">~{bombs['total_preventable_tokens']:,}</div>
        <div class="kpi-sub">{bombs['token_bomb_files_count']} heavy artifact(s)</div>
      </div>
    </div>

    {pools_html}

    <section class="card full">
      <h2>Recommended Routing Strategy</h2>
      <p><strong>Optimal Topology:</strong> {html.escape(comp['routing_decision']['recommended_topology'])}<br/>
      <strong>Target Tier:</strong> <code>{html.escape(comp['routing_decision']['recommended_model_tier'])}</code> •
      <strong>Projected Savings:</strong> <span class="pill ok">{html.escape(comp['routing_decision']['estimated_quota_savings'])}</span></p>
    </section>

    <section class="card full">
      <h2>Monolith vs. Multi-Agent Quota Simulation</h2>
      <table>
        <thead><tr><th>Strategy</th><th>Cumulative Input Tokens</th><th>Thinking Tokens</th><th>Quota Saved</th></tr></thead>
        <tbody>{''.join(sim_rows)}</tbody>
      </table>
    </section>

    <section class="card full">
      <h2>Collision-Free Parallel Worker Slices ({len(slices['stage_1_parallel_slices'])} Workers)</h2>
      <ul>{''.join(slice_items) or '<li>Single-module workspace — execute inline.</li>'}</ul>
    </section>
  </div>
</body>
</html>
"""


def main() -> int:
    _configure_utf8()
    parser = argparse.ArgumentParser(description="Generate a standalone interactive HTML quota & workspace telemetry dashboard.")
    parser.add_argument("--workspace", "-w", default=".", help="Workspace path to analyze.")
    parser.add_argument("--quota-json", "-q", help="Optional path to live swarm(action='models', all=true) JSON.")
    parser.add_argument("--output", "-o", default="quota-dashboard.html", help="Output HTML file path.")
    parser.add_argument("--task", "-t", default="Full-stack feature implementation & verification", help="Task description.")
    args = parser.parse_args()

    skills_root = Path(__file__).resolve().parents[2]
    ws = Path(args.workspace).resolve()
    q_path = Path(args.quota_json).resolve() if args.quota_json else None

    html_doc = build_dashboard_html(ws, skills_root, quota_json_path=q_path, task_desc=args.task)
    out_path = Path(args.output).resolve()
    out_path.write_text(html_doc, encoding="utf-8")
    print(f"[OK] Generated interactive dashboard: {str(out_path).replace(chr(92), '/')}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
