#!/usr/bin/env python3
"""Unified Master CLI (`sqo`) for Smart Quota & Superpowers OS v10.0 Apex Edition.

Provides 52 deterministic, zero-dependency commands for AI coding agents and developers:
  - symbol-edit     : Serena-Class Surgical Symbol-Level AST Mutator (-85% Output Tokens!)
  - callers         : Fast Cross-Repo Function/Method Call-Site Locator before signature edits
  - spec            : Spec-Kit + Taskmaster Autonomous Spec-Driven DAG & Gatekeeper
  - graph-mem       : Claude-Mem Auto-Captured Temporal Knowledge Graph & Mermaid Exporter
  - verify-work     : Executable Karpathy + Superpowers Diff, Laziness & Scope Auditor
  - sdk-radar       : Context7-Class Live Version-Pinned SDK Idioms & Deprecation Scanner
  - sandbox         : Superpowers Isolated Git Worktree / Snapshot Experiment Runner
  - serve           : Launch the Real-Time Localhost Web Command Center (http://127.0.0.1:7890)
  - init            : Auto-detect stack (Flutter/Next.js/Laravel/Python/Go/Rust) & bootstrap shields
  - verify-deps     : Anti-Hallucination Dependency & Phantom Import Verifier (Python/JS/TS/Dart)
  - i18n            : Universal Flutter .arb & JSON Localization Drift & Placeholder Auditor
  - memo            : SHA-256 Content-Hash Invalidated Semantic Memoization Cache (2ms hits!)
  - contracts       : Distill Backend Routes into Compact API Contracts + OpenAPI 3.1 JSON
  - swarm-plan      : Turnkey Multi-Model File-Disjoint Swarm Blueprint & Prompt Generator
  - hub             : Pull/Publish Golden AI Stack Rules via Live Cloud Hub (sqo.elnemer-ai.com)
  - hive            : Cross-Project Federated Hive-Mind Brain (`~/.sqo/hive_mind.db`) across all repos!
  - schema          : Universal 6-Stack DB & GraphQL Schema Distiller (94%-98% token compression!)
  - dry-run         : <12ms Pre-Flight Syntax, Delimiter, Import & Conflict Guard before builds
  - checkpoint      : Zero-Git-Conflict Session Time-Machine & Surgical File Rollback
  - ci-shield       : Generate GitHub Actions Pull Request Token & Secret Shield workflow
  - share           : Generate Live GitHub Profile Trophy SVG Card & sync to sqo.elnemer-ai.com
  - context-health  : Score quadratic Context-Rot risk (0-100) & emit <350-token handoff snapshot
  - compress-prompt : Compress verbose raw prompts, repetitive JSON arrays & logs (-55% to -85%)
  - badge           : Generate verified SVG token-efficiency shield badge (`sqo-badge.svg`)
  - doctor          : Full 8-in-1 workspace, KV-cache, secret-safety, ROI & graph health check
  - roi             : Live SQLite Token & Dollar ($USD) ROI Ledger of prevented waste
  - media           : Multi-Modal Image/PDF Vision Token Cost Estimator (Gemini/Claude/OpenAI)
  - git-guard       : Install <40ms Git pre-commit secret & prompt-tax shield
  - benchmark       : Live empirical Before-vs-After token compression benchmark
  - search          : SQLite FTS5 BM25 instant symbol & code-chunk search
  - hotspots        : Incremental SQLite Code Graph (Cyclomatic × Fan-In hotspots & orphans)
  - routes          : Multi-framework API & UI route table extractor (7 frameworks)
  - pinpoint        : 1-shot multi-file crash stack-trace code window extractor
  - pack            : Adaptive multi-file context packer (Full + AST Skeletons + Index)
  - blast-radius    : Transitive reverse-import impact & minimal affected test selector
  - memory          : Persistent SQLite FTS5 cross-session architectural memory vault
  - scrub           : Hardcoded secret scanner (masked) & pre-prompt secret redactor
  - cache-audit     : LLM Prompt KV-Cache prefix stability & cache-busting detector
  - sync-ide        : Wire MCP server & ignore shields across Antigravity, Cursor, Claude, VS Code & Windsurf
  - pools           : Group live model quotas, reset timers & failover reserves
  - complexity      : Score task complexity (0-100) & parallelizability (0.0-1.0)
  - simulate        : Compare monolithic vs Orchestrator vs workflow quota burn
  - slice           : Partition repo imports into collision-free parallel slices / workflow code
  - outline         : Extract compact AST/symbol line-range skeleton from huge files
  - diff            : Compress noisy git diffs into a strict token budget
  - denoise         : Strip 90%+ noise from test/build/linter CLI outputs
  - prompt-tax      : Audit AGENTS.md / CLAUDE.md / GEMINI.md / SKILL.md static token tax
  - ignore-guard    : Find context-bomb files & generate .agentignore / .cursorignore
  - audit           : Inspect active JSONL session transcripts for token leaks
  - handoff         : Generate a <400-token zero-loss state brief before /compact
  - dashboard       : Render a standalone dark-glassmorphism HTML telemetry dashboard
  - mcp             : Start the native JSON-RPC 2.0 Stdio MCP Server (31 live tools)
"""

from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path
from typing import Dict, List, Tuple

ROOT_DIR = Path(__file__).resolve().parent
SKILLS_DIR = ROOT_DIR / "skills"

COMMAND_MAP: Dict[str, Tuple[Path, List[str]]] = {
    "serve": (SKILLS_DIR / "smart-quota-orchestrator" / "scripts" / "live_server.py", []),
    "symbol-edit": (SKILLS_DIR / "apex-spec-surgeon" / "scripts" / "edit_symbol.py", []),
    "callers": (SKILLS_DIR / "apex-spec-surgeon" / "scripts" / "edit_symbol.py", ["--action", "callers"]),
    "spec": (SKILLS_DIR / "apex-spec-surgeon" / "scripts" / "spec_engine.py", []),
    "graph-mem": (SKILLS_DIR / "project-memory-vault" / "scripts" / "memory_graph.py", []),
    "verify-work": (SKILLS_DIR / "apex-spec-surgeon" / "scripts" / "verify_karpathy.py", []),
    "sdk-radar": (SKILLS_DIR / "apex-spec-surgeon" / "scripts" / "sdk_radar.py", []),
    "sandbox": (SKILLS_DIR / "apex-spec-surgeon" / "scripts" / "worktree_sandbox.py", []),
    "init": (SKILLS_DIR / "smart-quota-orchestrator" / "scripts" / "init_workspace_preset.py", []),
    "verify-deps": (SKILLS_DIR / "smart-quota-orchestrator" / "scripts" / "verify_hallucinations.py", []),
    "i18n": (SKILLS_DIR / "context-compactor" / "scripts" / "audit_i18n.py", []),
    "memo": (SKILLS_DIR / "smart-quota-orchestrator" / "scripts" / "semantic_cache.py", []),
    "contracts": (SKILLS_DIR / "context-compactor" / "scripts" / "extract_contracts.py", []),
    "swarm-plan": (SKILLS_DIR / "parallel-slice-architect" / "scripts" / "plan_swarm.py", []),
    "hub": (SKILLS_DIR / "smart-quota-orchestrator" / "scripts" / "cloud_hub.py", []),
    "hive": (SKILLS_DIR / "project-memory-vault" / "scripts" / "hive_mind.py", []),
    "schema": (SKILLS_DIR / "context-compactor" / "scripts" / "distill_schema.py", []),
    "dry-run": (SKILLS_DIR / "smart-quota-orchestrator" / "scripts" / "shadow_dry_run.py", []),
    "checkpoint": (SKILLS_DIR / "smart-quota-orchestrator" / "scripts" / "time_machine.py", []),
    "ci-shield": (SKILLS_DIR / "smart-quota-orchestrator" / "scripts" / "generate_ci_shield.py", []),
    "share": (SKILLS_DIR / "smart-quota-orchestrator" / "scripts" / "cloud_share.py", []),
    "context-health": (SKILLS_DIR / "smart-quota-orchestrator" / "scripts" / "check_context_rot.py", []),
    "badge": (SKILLS_DIR / "smart-quota-orchestrator" / "scripts" / "generate_repo_badge.py", []),
    "pools": (SKILLS_DIR / "smart-quota-orchestrator" / "scripts" / "parse_quota_pools.py", []),
    "complexity": (SKILLS_DIR / "smart-quota-orchestrator" / "scripts" / "analyze_task_complexity.py", []),
    "simulate": (SKILLS_DIR / "smart-quota-orchestrator" / "scripts" / "simulate_workflow_cost.py", []),
    "audit": (SKILLS_DIR / "smart-quota-orchestrator" / "scripts" / "audit_session_burn.py", []),
    "dashboard": (SKILLS_DIR / "smart-quota-orchestrator" / "scripts" / "generate_html_dashboard.py", []),
    "benchmark": (SKILLS_DIR / "smart-quota-orchestrator" / "scripts" / "benchmark_suite.py", []),
    "sync-ide": (SKILLS_DIR / "smart-quota-orchestrator" / "scripts" / "sync_ide_configs.py", []),
    "roi": (SKILLS_DIR / "smart-quota-orchestrator" / "scripts" / "roi_ledger.py", []),
    "git-guard": (SKILLS_DIR / "smart-quota-orchestrator" / "scripts" / "install_git_guard.py", []),
    "handoff": (SKILLS_DIR / "context-compactor" / "scripts" / "build_handoff_brief.py", []),
    "outline": (SKILLS_DIR / "context-compactor" / "scripts" / "smart_outline.py", []),
    "pack": (SKILLS_DIR / "context-compactor" / "scripts" / "pack_context_bundle.py", []),
    "diff": (SKILLS_DIR / "context-compactor" / "scripts" / "compress_git_diff.py", []),
    "denoise": (SKILLS_DIR / "context-compactor" / "scripts" / "compact_command_output.py", []),
    "ignore-guard": (SKILLS_DIR / "context-compactor" / "scripts" / "generate_agent_ignore.py", []),
    "media": (SKILLS_DIR / "context-compactor" / "scripts" / "estimate_media_tokens.py", []),
    "compress-prompt": (SKILLS_DIR / "context-compactor" / "scripts" / "compress_prompt.py", []),
    "search": (SKILLS_DIR / "semantic-code-navigator" / "scripts" / "search_code_bm25.py", []),
    "blast-radius": (SKILLS_DIR / "semantic-code-navigator" / "scripts" / "analyze_blast_radius.py", []),
    "hotspots": (SKILLS_DIR / "semantic-code-navigator" / "scripts" / "code_graph.py", ["hotspots"]),
    "routes": (SKILLS_DIR / "semantic-code-navigator" / "scripts" / "code_graph.py", ["routes"]),
    "pinpoint": (SKILLS_DIR / "semantic-code-navigator" / "scripts" / "pinpoint_stacktrace.py", []),
    "memory": (SKILLS_DIR / "project-memory-vault" / "scripts" / "memory_vault.py", []),
    "scrub": (SKILLS_DIR / "project-memory-vault" / "scripts" / "scrub_secrets.py", []),
    "slice": (SKILLS_DIR / "parallel-slice-architect" / "scripts" / "partition_parallel_slices.py", []),
    "prompt-tax": (SKILLS_DIR / "prompt-tax-profiler" / "scripts" / "optimize_prompt_rules.py", []),
    "cache-audit": (SKILLS_DIR / "prompt-tax-profiler" / "scripts" / "audit_cache_stability.py", []),
    "mcp": (ROOT_DIR / "mcp_server.py", []),
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
    print("# ⚡ Smart Quota & Swarm Orchestrator v9.0 — Omniscient Agent OS Doctor\n", flush=True)
    steps = [
        ("roi", []),
        ("prompt-tax", ["--workspace", ws]),
        ("cache-audit", ["--workspace", ws]),
        ("scrub", ["--scan-workspace", ws]),
        ("ignore-guard", ["--workspace", ws]),
        ("hotspots", ["--workspace", ws, "--top-k", "6"]),
        ("benchmark", ["--workspace", ws]),
        ("slice", ["--workspace", ws, "--max-workers", "4"]),
    ]
    for idx, (cmd_name, cmd_args) in enumerate(steps):
        if idx > 0:
            print("\n---\n", flush=True)
        script, preset = COMMAND_MAP[cmd_name]
        rc = _run_script(script, [*preset, *cmd_args])
        if rc != 0:
            return rc
    return 0


def _print_help() -> None:
    print(__doc__.strip())
    print("\nUsage:")
    print("  python sqo.py <subcommand> [options]\n")
    print("Quick Examples:")
    print("  npx -y smart-quota-orchestrator init --workspace .")
    print("  python sqo.py serve --workspace . --open")
    print("  python sqo.py compress-prompt --file noisy_log.txt")
    print("  python sqo.py badge --workspace .")
    print("  python sqo.py doctor --workspace .")


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

    script, preset = COMMAND_MAP[subcmd]
    return _run_script(script, [*preset, *rest])


if __name__ == "__main__":
    raise SystemExit(main())
