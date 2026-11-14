#!/usr/bin/env python3
"""Unified Master CLI (`sqo`) for Smart Quota & Swarm Orchestrator v3.0.

Provides 19 deterministic, zero-dependency commands for AI coding agents and developers:
  - doctor       : Full 6-in-1 workspace, secret-safety & prompt-tax health check
  - benchmark    : Live empirical Before-vs-After token compression benchmark
  - search       : SQLite FTS5 BM25 instant symbol & code-chunk search
  - pack         : Adaptive multi-file context packer (Full + AST Skeletons + Index)
  - blast-radius : Transitive reverse-import impact & minimal affected test selector
  - memory       : Persistent SQLite FTS5 cross-session architectural memory vault
  - scrub        : Hardcoded secret scanner (masked) & pre-prompt secret redactor
  - pools        : Group live model quotas, reset timers & failover reserves
  - complexity   : Score task complexity (0-100) & parallelizability (0.0-1.0)
  - simulate     : Compare monolithic vs Orchestrator vs workflow quota burn
  - slice        : Partition repo imports into collision-free parallel slices / workflow code
  - outline      : Extract compact AST/symbol line-range skeleton from huge files
  - diff         : Compress noisy git diffs into a strict token budget
  - denoise      : Strip 90%+ noise from test/build/linter CLI outputs
  - prompt-tax   : Audit AGENTS.md / CLAUDE.md / GEMINI.md / SKILL.md static token tax
  - ignore-guard : Find context-bomb files & generate .agentignore / .cursorignore
  - audit        : Inspect active JSONL session transcripts for token leaks
  - handoff      : Generate a <400-token zero-loss state brief before /compact
  - dashboard    : Render a standalone dark-glassmorphism HTML telemetry dashboard
  - mcp          : Start the native JSON-RPC 2.0 Stdio MCP Server (10 live tools)
"""

from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path
from typing import Dict, List

ROOT_DIR = Path(__file__).resolve().parent
SKILLS_DIR = ROOT_DIR / "skills"

COMMAND_MAP: Dict[str, Path] = {
    "pools": SKILLS_DIR / "smart-quota-orchestrator" / "scripts" / "parse_quota_pools.py",
    "complexity": SKILLS_DIR / "smart-quota-orchestrator" / "scripts" / "analyze_task_complexity.py",
    "simulate": SKILLS_DIR / "smart-quota-orchestrator" / "scripts" / "simulate_workflow_cost.py",
    "audit": SKILLS_DIR / "smart-quota-orchestrator" / "scripts" / "audit_session_burn.py",
    "dashboard": SKILLS_DIR / "smart-quota-orchestrator" / "scripts" / "generate_html_dashboard.py",
    "benchmark": SKILLS_DIR / "smart-quota-orchestrator" / "scripts" / "benchmark_suite.py",
    "handoff": SKILLS_DIR / "context-compactor" / "scripts" / "build_handoff_brief.py",
    "outline": SKILLS_DIR / "context-compactor" / "scripts" / "smart_outline.py",
    "pack": SKILLS_DIR / "context-compactor" / "scripts" / "pack_context_bundle.py",
    "diff": SKILLS_DIR / "context-compactor" / "scripts" / "compress_git_diff.py",
    "denoise": SKILLS_DIR / "context-compactor" / "scripts" / "compact_command_output.py",
    "ignore-guard": SKILLS_DIR / "context-compactor" / "scripts" / "generate_agent_ignore.py",
    "search": SKILLS_DIR / "semantic-code-navigator" / "scripts" / "search_code_bm25.py",
    "blast-radius": SKILLS_DIR / "semantic-code-navigator" / "scripts" / "analyze_blast_radius.py",
    "memory": SKILLS_DIR / "project-memory-vault" / "scripts" / "memory_vault.py",
    "scrub": SKILLS_DIR / "project-memory-vault" / "scripts" / "scrub_secrets.py",
    "slice": SKILLS_DIR / "parallel-slice-architect" / "scripts" / "partition_parallel_slices.py",
    "prompt-tax": SKILLS_DIR / "prompt-tax-profiler" / "scripts" / "optimize_prompt_rules.py",
    "mcp": ROOT_DIR / "mcp_server.py",
}


def _configure_utf8() -> None:
    for stream in (sys.stdout, sys.stderr):
        if hasattr(stream, "reconfigure"):
            try:
                stream.reconfigure(encoding="utf-8")
            except Exception:
                pass


def _run_script(script_path: Path, extra_args: List[str]) -> int:
    env = os.environ.copy()
    env["PYTHONIOENCODING"] = "utf-8"
    proc = subprocess.run([sys.executable, str(script_path), *extra_args], env=env, check=False)
    return proc.returncode


def _run_doctor(workspace_args: List[str]) -> int:
    ws = "."
    for i, tok in enumerate(workspace_args):
        if tok in ("-w", "--workspace") and i + 1 < len(workspace_args):
            ws = workspace_args[i + 1]
    print("# ⚡ Smart Quota & Swarm Orchestrator v3.0 — Full Autonomous Doctor\n", flush=True)
    steps = [
        ("prompt-tax", ["--workspace", ws]),
        ("scrub", ["--scan-workspace", ws]),
        ("ignore-guard", ["--workspace", ws]),
        ("benchmark", ["--workspace", ws]),
        ("complexity", ["--workspace", ws, "--task", "Workspace baseline readiness check"]),
        ("slice", ["--workspace", ws, "--max-workers", "4"]),
    ]
    for idx, (cmd_name, cmd_args) in enumerate(steps):
        if idx > 0:
            print("\n---\n", flush=True)
        rc = _run_script(COMMAND_MAP[cmd_name], cmd_args)
        if rc != 0:
            return rc
    return 0


def _print_help() -> None:
    print(__doc__.strip())
    print("\nUsage:")
    print("  python sqo.py <subcommand> [options]\n")
    print("Examples:")
    print("  python sqo.py doctor --workspace .")
    print("  python sqo.py benchmark --workspace .")
    print("  python sqo.py search \"verifyStripeWebhook jwt\" --workspace .")
    print("  python sqo.py pack --workspace . --max-tokens 3000")
    print("  python sqo.py blast-radius src/types/user.ts --workspace .")
    print("  python sqo.py memory --workspace . remember -c auth -t \"JWT Guard\" -d \"Uses RS256\"")


def main() -> int:
    _configure_utf8()
    if len(sys.argv) < 2 or sys.argv[1] in ("-h", "--help", "help"):
        _print_help()
        return 0

    subcmd = sys.argv[1].lower()
    rest = sys.argv[2:]

    if subcmd == "doctor":
        return _run_doctor(rest)

    if subcmd not in COMMAND_MAP:
        print(f"Unknown subcommand: '{subcmd}'. Available: doctor, {', '.join(sorted(COMMAND_MAP))}", file=sys.stderr)
        return 1

    return _run_script(COMMAND_MAP[subcmd], rest)


if __name__ == "__main__":
    raise SystemExit(main())
