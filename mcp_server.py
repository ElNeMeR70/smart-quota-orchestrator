#!/usr/bin/env python3
"""Zero-Dependency Model Context Protocol (MCP) Stdio Server (`sqo-engine` v11.0 Hypernova Edition).

Exposes 43 native, token-saving, Security SAST, N+1 Performance, RTL/UI & Superpowers tools directly to
Google Antigravity, Claude Code, Cursor, Windsurf, VS Code, and Gemini CLI over
JSON-RPC 2.0 `stdio` transport.

Blocks cleanly on `sys.stdin.readline()` when idle (0.0% idle CPU, <15 MB RAM).
Zero external `pip` packages required (100% Python 3.8+ standard library).
"""

from __future__ import annotations

import importlib.util
import json
import sys
import traceback
from pathlib import Path
from typing import Any, Dict, List

ROOT_DIR = Path(__file__).resolve().parent
SKILLS_DIR = ROOT_DIR / "skills"
SERVER_NAME = "sqo-engine"
SERVER_VERSION = "11.0.0"

_MOD_CACHE: Dict[str, Any] = {}


def _load_tool_mod(rel_path: str):
    if rel_path not in _MOD_CACHE:
        target = SKILLS_DIR / rel_path
        spec = importlib.util.spec_from_file_location(rel_path.replace("/", "_"), target)
        assert spec and spec.loader
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        _MOD_CACHE[rel_path] = mod
    return _MOD_CACHE[rel_path]


TOOLS_SPEC: List[Dict[str, Any]] = [
    {
        "name": "sqo_code_search",
        "description": "Instant SQLite FTS5 BM25 code & symbol chunk search. Returns top-K relevant functions/classes with exact file:Lstart-Lend coordinates in <250 tokens (90%+ savings vs grep + full reads).",
        "inputSchema": {
            "type": "object",
            "properties": {
                "workspace": {"type": "string", "description": "Absolute path to the workspace root directory."},
                "query": {"type": "string", "description": "Identifier, symbol, or natural-language code query."},
                "top_k": {"type": "integer", "description": "Number of top chunks to return (default: 6)."},
            },
            "required": ["workspace", "query"],
        },
    },
    {
        "name": "sqo_smart_outline",
        "description": "Extract compact AST/symbol signatures and Lstart-Lend line ranges from a large source file (saves 85-96% tokens vs reading full file), or extract one specific symbol body.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "file_path": {"type": "string", "description": "Absolute path to the file to outline."},
                "symbol": {"type": "string", "description": "Optional class/function/method name to extract with line numbers."},
            },
            "required": ["file_path"],
        },
    },
    {
        "name": "sqo_context_pack",
        "description": "Compile a multi-file directory or workspace into a strict token budget using full code for focus files and AST skeletons for supporting files.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "workspace": {"type": "string", "description": "Workspace root path."},
                "paths": {"type": "array", "items": {"type": "string"}, "description": "Optional subdirectories/files to scope."},
                "focus_files": {"type": "array", "items": {"type": "string"}, "description": "High-priority files kept in full source."},
                "max_tokens": {"type": "integer", "description": "Strict token ceiling (default: 3500)."},
            },
            "required": ["workspace"],
        },
    },
    {
        "name": "sqo_blast_radius",
        "description": "Trace transitive reverse-import dependents (who imports X) and return ONLY affected downstream files and minimal unit tests to run.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "workspace": {"type": "string", "description": "Workspace root path."},
                "targets": {"type": "array", "items": {"type": "string"}, "description": "Modified relative file paths."},
            },
            "required": ["workspace", "targets"],
        },
    },
    {
        "name": "sqo_pinpoint_error",
        "description": "Parse any multi-file crash stack trace (Python, Node/TS, Dart/Flutter, Go, Rust, PHP) and extract the exact +-10 line source window around every local workspace frame in 1 call.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "workspace": {"type": "string", "description": "Workspace root path."},
                "stack_trace": {"type": "string", "description": "Raw stack trace / traceback text."},
                "radius": {"type": "integer", "description": "Context lines above/below crash line (default: 10)."},
            },
            "required": ["workspace", "stack_trace"],
        },
    },
    {
        "name": "sqo_code_hotspots",
        "description": "Sync incremental mtime-cached SQLite code graph (<10ms warm) and return top Cyclomatic Complexity x Import Fan-In bug hotspots plus unreferenced orphan modules.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "workspace": {"type": "string", "description": "Workspace root path."},
                "top_k": {"type": "integer", "description": "Number of top hotspots to return (default: 10)."},
            },
            "required": ["workspace"],
        },
    },
    {
        "name": "sqo_api_routes",
        "description": "Extract complete Backend & UI Route table across Next.js, Express/Fastify, NestJS, FastAPI/Flask, Laravel, Go, and Flutter in <200 tokens.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "workspace": {"type": "string", "description": "Workspace root path."},
            },
            "required": ["workspace"],
        },
    },
    {
        "name": "sqo_memory_vault",
        "description": "Persistent cross-session SQLite FTS5 architectural memory bank (auto-injected at SessionStart!). Store ('remember') or BM25-query ('recall' / 'list') project facts.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "workspace": {"type": "string", "description": "Workspace root path."},
                "action": {"type": "string", "enum": ["remember", "recall", "list"], "description": "Vault operation."},
                "query": {"type": "string", "description": "BM25 search query (for 'recall')."},
                "category": {"type": "string", "description": "Category tag (architecture, auth, db, build, gotcha)."},
                "title": {"type": "string", "description": "Short fact headline (for 'remember')."},
                "detail": {"type": "string", "description": "Concise explanation (for 'remember')."},
                "files": {"type": "array", "items": {"type": "string"}, "description": "Related relative file paths."},
            },
            "required": ["workspace", "action"],
        },
    },
    {
        "name": "sqo_dependency_slices",
        "description": "Parse import dependency graphs into Stage-0 shared contracts and Stage-1 collision-free parallel worker slices (optionally emitting an Antigravity run_workflow script).",
        "inputSchema": {
            "type": "object",
            "properties": {
                "workspace": {"type": "string", "description": "Workspace root path."},
                "max_workers": {"type": "integer", "description": "Max parallel worker buckets (default: 4)."},
                "goal": {"type": "string", "description": "Task goal when emitting workflow code."},
                "emit_workflow": {"type": "boolean", "description": "Return ready-to-run Antigravity run_workflow Python code."},
            },
            "required": ["workspace"],
        },
    },
    {
        "name": "sqo_budgeted_diff",
        "description": "Compress working-tree git diff into a strict token ceiling, automatically stripping lockfiles, sourcemaps, and generated bundles.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "workspace": {"type": "string", "description": "Git repository path."},
                "max_tokens": {"type": "integer", "description": "Maximum token budget (default: 2000)."},
                "staged": {"type": "boolean", "description": "Inspect staged changes only."},
            },
            "required": ["workspace"],
        },
    },
    {
        "name": "sqo_secret_scrub",
        "description": "Audit workspace source files for hardcoded secrets (outputs safe masked fingerprints only) or redact secrets from text.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "workspace": {"type": "string", "description": "Workspace directory to audit for hardcoded secrets."},
                "text": {"type": "string", "description": "Optional raw text snippet to redact instead of scanning workspace."},
            },
        },
    },
    {
        "name": "sqo_cache_audit",
        "description": "Audit hooks, MCP tools, and rules for LLM Prompt KV-Cache prefix stability (ensuring 75%-90% prompt cache hit discounts).",
        "inputSchema": {
            "type": "object",
            "properties": {
                "workspace": {"type": "string", "description": "Workspace path to audit."},
            },
            "required": ["workspace"],
        },
    },
    {
        "name": "sqo_quota_pools",
        "description": "Analyze live model quota JSON into shared vs. independent reserve pools, reset countdowns, and safe %/hour burn rates.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "models_json": {"type": "string", "description": "Raw JSON string returned by swarm(action='models', all=true)."},
            },
            "required": ["models_json"],
        },
    },
    {
        "name": "sqo_benchmark",
        "description": "Run live empirical token-compression benchmarks on a workspace and return measured Before-vs-After savings.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "workspace": {"type": "string", "description": "Workspace path to benchmark."},
            },
            "required": ["workspace"],
        },
    },
    {
        "name": "sqo_roi_ledger",
        "description": "Query the live SQLite Token & Dollar ($USD) ROI Ledger showing cumulative tokens saved by the autonomous hook shield and MCP compression engines.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "db_path": {"type": "string", "description": "Optional custom roi_ledger.db path."},
            },
        },
    },
    {
        "name": "sqo_media_budget",
        "description": "Estimate multimodal vision & PDF input token costs (PNG, JPEG, WebP, GIF, PDF) across Gemini, Claude, and OpenAI and flag oversized 4K screenshots.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "workspace": {"type": "string", "description": "Workspace root directory."},
                "targets": {"type": "array", "items": {"type": "string"}, "description": "Optional media file or folder paths."},
            },
            "required": ["workspace"],
        },
    },
    {
        "name": "sqo_init_preset",
        "description": "Auto-detect workspace framework (Flutter, Next.js, Laravel, Python/FastAPI, Node/TS, Go, Rust) and bootstrap IDE MCP configs, framework ignore shields, starter memories & Git pre-commit guard.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "workspace": {"type": "string", "description": "Workspace root directory."},
                "preset": {"type": "string", "description": "Optional preset override ('auto', 'flutter', 'nextjs', 'laravel', 'fastapi-python', 'node-ts', 'go', 'rust')."},
            },
            "required": ["workspace"],
        },
    },
    {
        "name": "sqo_context_health",
        "description": "Measure quadratic session Context-Rot risk (0-100) on the active conversation transcript and emit a ready-to-paste <350-token Zero-Loss Handoff Snapshot.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "workspace": {"type": "string", "description": "Workspace root directory."},
                "goal": {"type": "string", "description": "Current engineering goal for the handoff snapshot."},
            },
            "required": ["workspace"],
        },
    },
    {
        "name": "sqo_compress_prompt",
        "description": "Deterministically compress verbose raw text, repetitive JSON arrays, and noisy log pastes by 55%-85% while scrubbing accidental API keys/secrets.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "text": {"type": "string", "description": "Raw prompt, JSON dump, or log text to compress and scrub."},
            },
            "required": ["text"],
        },
    },
    {
        "name": "sqo_repo_badge",
        "description": "Generate a verified Smart Quota OS SVG shield badge (`sqo-badge.svg`) displaying the repository's empirical token reduction % and prompt-tax grade.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "workspace": {"type": "string", "description": "Workspace root directory."},
                "output_path": {"type": "string", "description": "Optional output SVG file path (default: sqo-badge.svg in workspace)."},
            },
            "required": ["workspace"],
        },
    },
    {
        "name": "sqo_hive_mind",
        "description": "Cross-Project Federated Brain (`~/.sqo/hive_mind.db`): promote architectural wisdom/gotchas across repos, recall stack-specific lessons (`flutter`, `nextjs`, `laravel`, `python`), or inject global lessons into a new project.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "action": {"type": "string", "enum": ["promote", "recall", "inject", "stats"], "description": "Hive-Mind operation."},
                "workspace": {"type": "string", "description": "Workspace root directory."},
                "stack": {"type": "string", "description": "Optional stack filter ('auto', 'flutter', 'nextjs', 'laravel', 'python', 'universal')."},
                "query": {"type": "string", "description": "BM25 search query when action='recall'."},
                "title": {"type": "string", "description": "Direct lesson title when promoting a new gotcha."},
                "detail": {"type": "string", "description": "Direct lesson detail when promoting a new gotcha."},
            },
            "required": ["action"],
        },
    },
    {
        "name": "sqo_schema_distill",
        "description": "Universal 6-Stack Database & GraphQL Schema Distiller: compresses 30k-90k tokens of SQL DDL, Prisma, Laravel migrations, Flutter Drift/Sqflite, SQLAlchemy, or GraphQL schemas into a <350-token Entity-Relationship DSL + Mermaid diagram.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "workspace": {"type": "string", "description": "Workspace root directory or schema file path."},
            },
            "required": ["workspace"],
        },
    },
    {
        "name": "sqo_shadow_check",
        "description": "Speculative <12ms Pre-Flight Syntax, Balanced Delimiter, Broken Relative Import & Merge-Conflict Guard across Python, JSON, TS/JS, Dart, PHP, Go, and Rust BEFORE running expensive builds/tests.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "workspace": {"type": "string", "description": "Workspace root directory."},
                "targets": {"type": "array", "items": {"type": "string"}, "description": "Optional file/folder paths (defaults to git dirty files)."},
            },
            "required": ["workspace"],
        },
    },
    {
        "name": "sqo_checkpoint",
        "description": "Zero-Git-Conflict Session Time-Machine: create instant zlib-compressed source snapshots, diff live edits against a checkpoint, or surgically roll back files without touching Git history.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "action": {"type": "string", "enum": ["create", "list", "diff", "restore"], "description": "Checkpoint action."},
                "workspace": {"type": "string", "description": "Workspace root directory."},
                "label": {"type": "string", "description": "Checkpoint label when action='create'."},
                "checkpoint_id": {"type": "string", "description": "Checkpoint ID (or 'latest') for diff/restore."},
                "files": {"type": "array", "items": {"type": "string"}, "description": "Optional relative file subset to snapshot or restore."},
            },
            "required": ["action", "workspace"],
        },
    },
    {
        "name": "sqo_ci_shield",
        "description": "Generate `.github/workflows/sqo-shield.yml` GitHub Actions Pull Request Shield to enforce zero secret leaks, pre-flight syntax checks, KV-cache stability, and vision media budgets on every PR.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "workspace": {"type": "string", "description": "Workspace root directory."},
            },
            "required": ["workspace"],
        },
    },
    {
        "name": "sqo_verify_deps",
        "description": "Anti-Hallucination Dependency & Phantom Import Verifier: cross-checks source imports across Python, JS/TS, and Dart/Flutter against package.json, pubspec.yaml, pyproject.toml, and requirements.txt to catch hallucinated/undeclared packages before build!",
        "inputSchema": {
            "type": "object",
            "properties": {
                "workspace": {"type": "string", "description": "Workspace root directory."},
            },
            "required": ["workspace"],
        },
    },
    {
        "name": "sqo_i18n_audit",
        "description": "Universal Localization / i18n Drift & Placeholder Auditor: checks Flutter `.arb` and `locales/*.json` bundles for missing translation keys and `{var}` placeholder mismatches in <200 tokens (-97% vs reading raw locale files).",
        "inputSchema": {
            "type": "object",
            "properties": {
                "workspace": {"type": "string", "description": "Workspace root directory."},
            },
            "required": ["workspace"],
        },
    },
    {
        "name": "sqo_memo_cache",
        "description": "SHA-256 Content-Hash Invalidated Semantic Memoization Cache: stores/retrieves expensive subsystem analyses in 2ms (100% token savings) and auto-invalidates when any bound source file changes on disk.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "action": {"type": "string", "enum": ["get", "put", "stats"], "description": "Memoization cache operation."},
                "workspace": {"type": "string", "description": "Workspace root directory."},
                "question": {"type": "string", "description": "Analytical question or lookup key."},
                "answer": {"type": "string", "description": "Synthesized answer to cache when action='put'."},
                "files": {"type": "array", "items": {"type": "string"}, "description": "Source files whose SHA-256 hashes validate this cached answer."},
            },
            "required": ["action", "workspace"],
        },
    },
    {
        "name": "sqo_api_contracts",
        "description": "Spec-Driven Backend-to-Frontend API Contract & OpenAPI 3.1 Extractor: distills HTTP endpoints and path parameters into a <350-token Contract Table + OpenAPI 3.1 JSON so mobile/frontend agents never need to read backend controllers.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "workspace": {"type": "string", "description": "Backend workspace root directory."},
            },
            "required": ["workspace"],
        },
    },
    {
        "name": "sqo_swarm_plan",
        "description": "Autonomous Multi-Agent Swarm Brief & Model-Routing Planner: partitions any goal into Stage-0 Shared Contracts (Frontier model) + collision-free Stage-1 Parallel Workers (Fast model, -82% quota burn) with ready-to-send prompts.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "workspace": {"type": "string", "description": "Workspace root directory."},
                "goal": {"type": "string", "description": "Engineering feature or refactor goal."},
                "max_workers": {"type": "integer", "description": "Max parallel workers (default: 4)."},
            },
            "required": ["workspace", "goal"],
        },
    },
    {
        "name": "sqo_cloud_hub",
        "description": "Global Smart Quota Community Hub (`https://sqo.elnemer-ai.com/api/presets.php`): list, pull, or publish battle-tested Golden AI Rules & Gotchas for Flutter, Next.js, Laravel, Python, Rust & Go.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "action": {"type": "string", "enum": ["list", "pull", "publish"], "description": "Cloud Hub action."},
                "workspace": {"type": "string", "description": "Workspace root directory."},
                "stack": {"type": "string", "description": "Tech stack ('auto', 'flutter', 'nextjs', 'laravel', 'python', 'rust', 'go')."},
                "title": {"type": "string", "description": "Rule title when action='publish'."},
                "rule": {"type": "string", "description": "Golden rule snippet when action='publish'."},
            },
            "required": ["action"],
        },
    },
    {
        "name": "sqo_edit_symbol",
        "description": "Serena-Class Surgical Symbol-Level AST Mutator (v10.0): edits exact functions, classes, or Class.method symbols by name (-85% Output Tokens!) with automatic Time-Machine backup and <8ms syntax auto-rollback.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "workspace": {"type": "string", "description": "Workspace root directory."},
                "file_path": {"type": "string", "description": "Target source file path."},
                "symbol": {"type": "string", "description": "Symbol or Class.method name to mutate."},
                "action": {"type": "string", "enum": ["replace", "insert_after", "insert_before", "delete"], "description": "Mutation operation."},
                "code": {"type": "string", "description": "Replacement or inserted source block."},
            },
            "required": ["workspace", "file_path", "symbol", "action"],
        },
    },
    {
        "name": "sqo_find_callers",
        "description": "Fast Cross-Repo Symbol Call-Site Locator (v10.0): finds all call sites and definitions of a function or method before changing its signature.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "workspace": {"type": "string", "description": "Workspace root directory."},
                "symbol": {"type": "string", "description": "Function or method name."},
                "max_hits": {"type": "integer", "description": "Max call sites to return (default: 25)."},
            },
            "required": ["workspace", "symbol"],
        },
    },
    {
        "name": "sqo_spec_engine",
        "description": "Spec-Kit + Taskmaster Autonomous Spec-Driven DAG Engine (v10.0): manages `.sqo/specs.db` atomic task graphs with file-ownership locks, <220-token `next` task briefs, and mandatory verification command gates.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "action": {"type": "string", "enum": ["init", "next", "complete", "status"], "description": "Spec DAG action."},
                "workspace": {"type": "string", "description": "Workspace root directory."},
                "slug": {"type": "string", "description": "Spec slug (optional for next/status)."},
                "title": {"type": "string", "description": "Feature title when action='init'."},
                "goal": {"type": "string", "description": "Feature goal when action='init'."},
                "step_key": {"type": "string", "description": "Task step_key (e.g. 'T1') when action='complete'."},
                "tasks": {"type": "array", "items": {"type": "object"}, "description": "Optional task objects for action='init'."},
            },
            "required": ["action", "workspace"],
        },
    },
    {
        "name": "sqo_memory_graph",
        "description": "Claude-Mem + Graphiti Auto-Captured Temporal Knowledge Graph (v10.0): queries `.sqo/memory_graph.db` co-edit & bugfix relationships per file or exports Mermaid architecture memory diagrams.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "action": {"type": "string", "enum": ["summary", "file_history", "record"], "description": "Knowledge graph operation."},
                "workspace": {"type": "string", "description": "Workspace root directory."},
                "file": {"type": "string", "description": "Relative file path for file_history or record."},
                "note": {"type": "string", "description": "Architectural or bugfix note when action='record'."},
            },
            "required": ["action", "workspace"],
        },
    },
    {
        "name": "sqo_verify_work",
        "description": "Executable Andrej Karpathy + Superpowers Diff Gatekeeper (v10.0): audits git diffs for TODO/placeholder laziness, silent public symbol deletions, out-of-scope file creep, and bloat, returning a 0-100 Surgical Discipline Score.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "workspace": {"type": "string", "description": "Workspace root directory."},
                "diff_text": {"type": "string", "description": "Optional unified diff override."},
                "allowed_files": {"type": "array", "items": {"type": "string"}, "description": "Optional list of allowed file/folder scopes."},
            },
            "required": ["workspace"],
        },
    },
    {
        "name": "sqo_sdk_radar",
        "description": "Context7-Class Live Version-Pinned SDK Idioms & Deprecation Radar (v10.0): reads installed package versions (`package.json`, `pubspec.yaml`, `pyproject.toml`) and detects deprecated 2023/2024 API hallucinations with modern fixes.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "workspace": {"type": "string", "description": "Workspace root directory."},
            },
            "required": ["workspace"],
        },
    },
    {
        "name": "sqo_worktree_sandbox",
        "description": "Superpowers Isolated Experiment Sandbox (v10.0): creates zero-risk Git worktree / snapshot sandboxes under `.sqo/sandboxes/<name>`, diffs changes, promotes verified files, or cleans up cleanly.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "action": {"type": "string", "enum": ["create", "diff", "promote", "cleanup", "list"], "description": "Sandbox operation."},
                "workspace": {"type": "string", "description": "Workspace root directory."},
                "name": {"type": "string", "description": "Sandbox name (e.g. 'exp-auth')."},
            },
            "required": ["action", "workspace"],
        },
    },
    {
        "name": "sqo_security_audit",
        "description": "OWASP Top-10 & Agentic SAST Vulnerability Scanner (v11.0 Hypernova): scans Python, TS/JS, PHP/Laravel, Dart & Go for SQL Injection (CWE-89), Command Injection (CWE-78), XSS (CWE-79), Eval/Pickle RCE (CWE-95), Weak Crypto & CORS bugs in <15ms!",
        "inputSchema": {
            "type": "object",
            "properties": {
                "workspace": {"type": "string", "description": "Workspace root directory."},
            },
            "required": ["workspace"],
        },
    },
    {
        "name": "sqo_perf_audit",
        "description": "Database N+1 Query, Sequential Async Waterfall & Flutter UI-Jank Profiler (v11.0 Hypernova): catches N+1 DB/HTTP calls inside loops, unbatched sequential awaits, undisposed Flutter controllers, and jsonDecode in build().",
        "inputSchema": {
            "type": "object",
            "properties": {
                "workspace": {"type": "string", "description": "Workspace root directory."},
            },
            "required": ["workspace"],
        },
    },
    {
        "name": "sqo_gen_tests",
        "description": "Zero-Token Deterministic Unit & Edge-Case Test Synthesizer (v11.0 Hypernova): parses Python, TS/JS, or Dart source files and generates ready-to-run Red-Green TDD test harnesses (saving ~3,000 Output Tokens per module!).",
        "inputSchema": {
            "type": "object",
            "properties": {
                "file_path": {"type": "string", "description": "Target source file path."},
                "output_path": {"type": "string", "description": "Optional path to write generated test file."},
            },
            "required": ["file_path"],
        },
    },
    {
        "name": "sqo_ui_audit",
        "description": "Bilingual Arabic RTL, WCAG Accessibility & Flutter RenderFlex Overflow Auditor (v11.0 Hypernova): catches hardcoded physical left/right directions, missing image alt labels, and unwrapped Text inside Flutter Row().",
        "inputSchema": {
            "type": "object",
            "properties": {
                "workspace": {"type": "string", "description": "Workspace root directory."},
            },
            "required": ["workspace"],
        },
    },
    {
        "name": "sqo_drift_guard",
        "description": "Environment Variable & Config Drift Detector (v11.0 Hypernova): cross-checks all `process.env`, `os.getenv`, `env()`, and `String.fromEnvironment` references in code against `.env.example` to prevent production boot crashes.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "workspace": {"type": "string", "description": "Workspace root directory."},
            },
            "required": ["workspace"],
        },
    },
]


def _dispatch_tool(name: str, args: Dict[str, Any]) -> str:
    if name == "sqo_code_search":
        mod = _load_tool_mod("semantic-code-navigator/scripts/search_code_bm25.py")
        res = mod.search_workspace(Path(args["workspace"]).resolve(), args["query"], top_k=int(args.get("top_k", 6)))
        return mod.render_markdown(res)

    if name == "sqo_smart_outline":
        mod = _load_tool_mod("context-compactor/scripts/smart_outline.py")
        fpath = Path(args["file_path"]).resolve()
        outline = mod.build_outline(fpath)
        if args.get("symbol"):
            hit = mod.extract_symbol_source(fpath, outline, str(args["symbol"]))
            if hit:
                return f"### `{hit['symbol']}` (`L{hit['start_line']}-L{hit['end_line']}`)\n```\n{hit['code']}\n```"
        return mod.render_markdown(outline)

    if name == "sqo_context_pack":
        mod = _load_tool_mod("context-compactor/scripts/pack_context_bundle.py")
        res = mod.pack_context(
            Path(args["workspace"]).resolve(),
            args.get("paths") or [],
            args.get("focus_files") or [],
            max_tokens=int(args.get("max_tokens", 3500)),
        )
        return mod.render_markdown(res)

    if name == "sqo_blast_radius":
        mod = _load_tool_mod("semantic-code-navigator/scripts/analyze_blast_radius.py")
        res = mod.compute_blast_radius(Path(args["workspace"]).resolve(), list(args["targets"]))
        return mod.render_markdown(res)

    if name == "sqo_pinpoint_error":
        mod = _load_tool_mod("semantic-code-navigator/scripts/pinpoint_stacktrace.py")
        res = mod.pinpoint_trace(Path(args["workspace"]).resolve(), str(args["stack_trace"]), radius=int(args.get("radius", 10)))
        return mod.render_markdown(res)

    if name == "sqo_code_hotspots":
        mod = _load_tool_mod("semantic-code-navigator/scripts/code_graph.py")
        res = mod.analyze_hotspots(Path(args["workspace"]).resolve(), top_k=int(args.get("top_k", 10)))
        return mod.render_hotspots_md(res)

    if name == "sqo_api_routes":
        mod = _load_tool_mod("semantic-code-navigator/scripts/code_graph.py")
        res = mod.extract_all_routes(Path(args["workspace"]).resolve())
        return mod.render_routes_md(res)

    if name == "sqo_memory_vault":
        mod = _load_tool_mod("project-memory-vault/scripts/memory_vault.py")
        db_path = mod._resolve_db_path(Path(args["workspace"]).resolve())
        act = args["action"]
        if act == "remember":
            saved = mod.remember_fact(
                db_path,
                args.get("category", "architecture"),
                args.get("title", "Architecture Note"),
                args.get("detail", ""),
                args.get("files") or [],
            )
            return f"[OK] Stored Memory `#{saved['id']}`: **{saved['title']}**"
        if act == "recall":
            items = mod.recall_facts(db_path, args.get("query", ""), limit=8)
            return mod.render_memories_md(items, f"Recalled Memories for '{args.get('query', '')}'")
        items = mod.list_facts(db_path, category=args.get("category", ""), limit=20)
        return mod.render_memories_md(items, "Project Memory Vault")

    if name == "sqo_dependency_slices":
        mod = _load_tool_mod("parallel-slice-architect/scripts/partition_parallel_slices.py")
        plan = mod.partition_workspace(Path(args["workspace"]).resolve(), [], max_workers=int(args.get("max_workers", 4)))
        if args.get("emit_workflow"):
            return mod.emit_workflow_script(plan, args.get("goal", ""))
        return mod.render_markdown(plan)

    if name == "sqo_budgeted_diff":
        mod = _load_tool_mod("context-compactor/scripts/compress_git_diff.py")
        raw = mod._run_git_diff(Path(args["workspace"]).resolve(), "HEAD", bool(args.get("staged", False)))
        return mod.render_markdown(mod.compress_diff(raw, max_tokens=int(args.get("max_tokens", 2000))))

    if name == "sqo_secret_scrub":
        mod = _load_tool_mod("project-memory-vault/scripts/scrub_secrets.py")
        if args.get("text"):
            return mod.scrub_text(str(args["text"]))["scrubbed_text"]
        rep = mod.scan_workspace_secrets(Path(args.get("workspace", ".")).resolve())
        return json.dumps(rep, indent=2, ensure_ascii=False)

    if name == "sqo_cache_audit":
        mod = _load_tool_mod("prompt-tax-profiler/scripts/audit_cache_stability.py")
        rep = mod.audit_cache_stability(Path(args["workspace"]).resolve())
        return mod.render_markdown(rep)

    if name == "sqo_quota_pools":
        mod = _load_tool_mod("smart-quota-orchestrator/scripts/parse_quota_pools.py")
        rep = mod.analyze_pools(json.loads(args["models_json"]))
        return mod.render_markdown(rep)

    if name == "sqo_benchmark":
        mod = _load_tool_mod("smart-quota-orchestrator/scripts/benchmark_suite.py")
        rep = mod.run_live_benchmark(Path(args["workspace"]).resolve(), SKILLS_DIR)
        return mod.render_markdown(rep)

    if name == "sqo_roi_ledger":
        mod = _load_tool_mod("smart-quota-orchestrator/scripts/roi_ledger.py")
        db_p = mod.default_ledger_path(args.get("db_path"))
        return mod.render_markdown(mod.summarize_roi(db_p))

    if name == "sqo_media_budget":
        mod = _load_tool_mod("context-compactor/scripts/estimate_media_tokens.py")
        rep = mod.scan_media_paths(args.get("targets") or [], Path(args["workspace"]).resolve())
        return mod.render_markdown(rep)

    if name == "sqo_init_preset":
        mod = _load_tool_mod("smart-quota-orchestrator/scripts/init_workspace_preset.py")
        rep = mod.initialize_workspace(Path(args["workspace"]).resolve(), preset=str(args.get("preset", "auto")))
        return mod.render_markdown(rep)

    if name == "sqo_context_health":
        mod = _load_tool_mod("smart-quota-orchestrator/scripts/check_context_rot.py")
        rep = mod.evaluate_context_health(Path(args["workspace"]).resolve(), goal=str(args.get("goal", "Continue active implementation")))
        return mod.render_markdown(rep)

    if name == "sqo_compress_prompt":
        mod = _load_tool_mod("context-compactor/scripts/compress_prompt.py")
        rep = mod.compress_raw_prompt(str(args["text"]))
        return (
            f"Compressed `~{rep['original_tokens']}` -> `~{rep['compressed_tokens']}` tokens (`-{rep['savings_pct']}%`, `{rep['secrets_redacted']}` secrets redacted):\n\n"
            f"{rep['compressed_text']}"
        )

    if name == "sqo_repo_badge":
        mod = _load_tool_mod("smart-quota-orchestrator/scripts/generate_repo_badge.py")
        ws = Path(args["workspace"]).resolve()
        svg, meta = mod.build_badge_svg(ws)
        out = Path(args["output_path"]) if args.get("output_path") else (ws / "sqo-badge.svg")
        out.write_text(svg, encoding="utf-8")
        return f"[OK] Generated SVG badge (`-{meta['reduction_pct']}% Tokens | Grade {meta['grade']}`) at `{out}`"

    if name == "sqo_hive_mind":
        mod = _load_tool_mod("project-memory-vault/scripts/hive_mind.py")
        hive_db = mod.default_hive_path()
        act = str(args.get("action", "stats"))
        ws = Path(args.get("workspace", ".")).resolve()
        stack = str(args.get("stack", "auto"))
        if act == "promote":
            if args.get("title") and args.get("detail"):
                st = mod.detect_stack(ws) if stack == "auto" else stack
                res = mod.store_hive_lesson(hive_db, st, "architecture", str(args["title"]), str(args["detail"]), source_repo=ws.name)
            else:
                res = mod.promote_from_workspace(ws, hive_db, stack=stack)
            return json.dumps(res, indent=2, ensure_ascii=False)
        if act == "inject":
            return json.dumps(mod.inject_into_workspace(ws, hive_db, stack=stack), indent=2, ensure_ascii=False)
        st_filter = "" if stack in ("auto", "all") else stack
        items = mod.recall_hive(hive_db, query=str(args.get("query", "")), stack=st_filter, limit=10)
        return mod.render_markdown(items, mod.hive_stats(hive_db))

    if name == "sqo_schema_distill":
        mod = _load_tool_mod("context-compactor/scripts/distill_schema.py")
        return mod.render_markdown(mod.distill_workspace_schema(Path(args["workspace"]).resolve()))

    if name == "sqo_shadow_check":
        mod = _load_tool_mod("smart-quota-orchestrator/scripts/shadow_dry_run.py")
        return mod.render_markdown(mod.run_shadow_check(Path(args["workspace"]).resolve(), args.get("targets")))

    if name == "sqo_checkpoint":
        mod = _load_tool_mod("smart-quota-orchestrator/scripts/time_machine.py")
        ws = Path(args["workspace"]).resolve()
        act = str(args["action"])
        cp_id = str(args.get("checkpoint_id", "latest"))
        if act == "create":
            res = mod.create_checkpoint(ws, label=str(args.get("label", "agent-step")), files_filter=args.get("files"))
        elif act == "diff":
            res = mod.diff_checkpoint(ws, cp_id=cp_id)
        elif act == "restore":
            res = mod.restore_checkpoint(ws, cp_id=cp_id, files_filter=args.get("files"))
        else:
            res = {"checkpoints": mod.list_checkpoints(ws)}
        return json.dumps(res, indent=2, ensure_ascii=False)

    if name == "sqo_ci_shield":
        mod = _load_tool_mod("smart-quota-orchestrator/scripts/generate_ci_shield.py")
        return json.dumps(mod.install_ci_shield(Path(args["workspace"]).resolve()), indent=2, ensure_ascii=False)

    if name == "sqo_verify_deps":
        mod = _load_tool_mod("smart-quota-orchestrator/scripts/verify_hallucinations.py")
        return mod.render_markdown(mod.verify_workspace_dependencies(Path(args["workspace"]).resolve()))

    if name == "sqo_i18n_audit":
        mod = _load_tool_mod("context-compactor/scripts/audit_i18n.py")
        return mod.render_markdown(mod.audit_workspace_i18n(Path(args["workspace"]).resolve()))

    if name == "sqo_memo_cache":
        mod = _load_tool_mod("smart-quota-orchestrator/scripts/semantic_cache.py")
        ws = Path(args["workspace"]).resolve()
        act = str(args["action"])
        if act == "put":
            res = mod.memo_put(ws, str(args.get("question", "")), str(args.get("answer", "")), args.get("files") or [])
        elif act == "get":
            res = mod.memo_get(ws, str(args.get("question", "")))
        else:
            res = mod.memo_stats(ws)
        return json.dumps(res, indent=2, ensure_ascii=False)

    if name == "sqo_api_contracts":
        mod = _load_tool_mod("context-compactor/scripts/extract_contracts.py")
        return mod.render_markdown(mod.extract_api_contracts(Path(args["workspace"]).resolve()))

    if name == "sqo_swarm_plan":
        mod = _load_tool_mod("parallel-slice-architect/scripts/plan_swarm.py")
        bp = mod.build_swarm_blueprint(Path(args["workspace"]).resolve(), str(args["goal"]), max_workers=int(args.get("max_workers", 4)))
        return mod.render_markdown(bp)

    if name == "sqo_cloud_hub":
        mod = _load_tool_mod("smart-quota-orchestrator/scripts/cloud_hub.py")
        act = str(args.get("action", "list"))
        ws = Path(args.get("workspace", ".")).resolve()
        st = str(args.get("stack", "auto"))
        if act == "pull":
            res = mod.pull_into_workspace(ws, stack=st)
        elif act == "publish":
            res = mod.publish_hub_rule(st, str(args.get("title", "")), str(args.get("rule", "")))
        else:
            res = mod.fetch_hub_presets("" if st in ("auto", "all") else st)
        return json.dumps(res, indent=2, ensure_ascii=False)

    if name == "sqo_edit_symbol":
        mod = _load_tool_mod("apex-spec-surgeon/scripts/edit_symbol.py")
        ws = Path(args["workspace"]).resolve()
        fp = Path(args["file_path"])
        fpath = fp if fp.is_absolute() else (ws / fp)
        res = mod.mutate_symbol(ws, fpath, str(args["symbol"]), str(args["action"]), str(args.get("code", "")))
        return mod.render_markdown(res)

    if name == "sqo_find_callers":
        mod = _load_tool_mod("apex-spec-surgeon/scripts/edit_symbol.py")
        res = mod.find_callers(Path(args["workspace"]).resolve(), str(args["symbol"]), max_hits=int(args.get("max_hits", 25)))
        return mod.render_markdown(res)

    if name == "sqo_spec_engine":
        mod = _load_tool_mod("apex-spec-surgeon/scripts/spec_engine.py")
        ws = Path(args["workspace"]).resolve()
        act = str(args["action"])
        slug = str(args.get("slug", ""))
        if act == "init":
            res = mod.init_spec(ws, str(args.get("title", "Feature")), str(args.get("goal", "")), tasks=args.get("tasks"))
        elif act == "next":
            res = mod.get_next_task(ws, slug)
        elif act == "complete":
            res = mod.complete_task(ws, slug, str(args.get("step_key", "T1")))
        else:
            res = mod.spec_status(ws, slug)
        return mod.render_markdown(res)

    if name == "sqo_memory_graph":
        mod = _load_tool_mod("project-memory-vault/scripts/memory_graph.py")
        ws = Path(args["workspace"]).resolve()
        act = str(args["action"])
        if act == "file_history":
            res = mod.query_file_history(ws, str(args.get("file", "")))
        elif act == "record":
            res = mod.record_auto_observation(ws, "rule", file_rel=str(args.get("file", "")), note=str(args.get("note", "")))
            return json.dumps(res, indent=2, ensure_ascii=False)
        else:
            res = mod.graph_summary(ws)
        return mod.render_markdown(res)

    if name == "sqo_verify_work":
        mod = _load_tool_mod("apex-spec-surgeon/scripts/verify_karpathy.py")
        res = mod.verify_workspace_work(
            Path(args["workspace"]).resolve(),
            diff_override=str(args.get("diff_text", "")),
            allowed_files=args.get("allowed_files"),
        )
        return mod.render_markdown(res)

    if name == "sqo_sdk_radar":
        mod = _load_tool_mod("apex-spec-surgeon/scripts/sdk_radar.py")
        return mod.render_markdown(mod.scan_sdk_deprecations(Path(args["workspace"]).resolve()))

    if name == "sqo_worktree_sandbox":
        mod = _load_tool_mod("apex-spec-surgeon/scripts/worktree_sandbox.py")
        ws = Path(args["workspace"]).resolve()
        act = str(args["action"])
        sb_name = str(args.get("name", "exp-1"))
        if act == "create":
            res = mod.create_sandbox(ws, sb_name)
        elif act == "diff":
            res = mod.diff_sandbox(ws, sb_name)
        elif act == "promote":
            res = mod.promote_sandbox(ws, sb_name)
        elif act == "cleanup":
            res = mod.cleanup_sandbox(ws, sb_name)
        else:
            res = mod.list_sandboxes(ws)
        return json.dumps(res, indent=2, ensure_ascii=False)

    if name == "sqo_security_audit":
        mod = _load_tool_mod("apex-spec-surgeon/scripts/security_sast.py")
        return mod.render_markdown(mod.scan_workspace_security(Path(args["workspace"]).resolve()))

    if name == "sqo_perf_audit":
        mod = _load_tool_mod("apex-spec-surgeon/scripts/perf_profiler.py")
        return mod.render_markdown(mod.profile_workspace_performance(Path(args["workspace"]).resolve()))

    if name == "sqo_gen_tests":
        mod = _load_tool_mod("apex-spec-surgeon/scripts/test_synthesizer.py")
        out_p = Path(args["output_path"]).resolve() if args.get("output_path") else None
        return mod.render_markdown(mod.synthesize_tests_for_file(Path(args["file_path"]).resolve(), write_to=out_p))

    if name == "sqo_ui_audit":
        mod = _load_tool_mod("apex-spec-surgeon/scripts/ui_rtl_auditor.py")
        return mod.render_markdown(mod.audit_workspace_ui(Path(args["workspace"]).resolve()))

    if name == "sqo_drift_guard":
        mod = _load_tool_mod("context-compactor/scripts/detect_drift.py")
        return mod.render_markdown(mod.audit_env_and_config_drift(Path(args["workspace"]).resolve()))

    raise ValueError(f"Unknown MCP tool: {name}")


def _send(msg: Dict[str, Any]) -> None:
    sys.stdout.write(json.dumps(msg, ensure_ascii=False) + "\n")
    sys.stdout.flush()


def handle_rpc_message(req: Dict[str, Any]) -> Dict[str, Any] | None:
    method = req.get("method", "")
    req_id = req.get("id")

    if req_id is None:
        return None

    if method == "initialize":
        client_proto = (req.get("params") or {}).get("protocolVersion") or "2024-11-05"
        return {
            "jsonrpc": "2.0",
            "id": req_id,
            "result": {
                "protocolVersion": client_proto,
                "capabilities": {"tools": {}, "resources": {}},
                "serverInfo": {"name": SERVER_NAME, "version": SERVER_VERSION},
            },
        }

    if method == "ping":
        return {"jsonrpc": "2.0", "id": req_id, "result": {}}

    if method == "tools/list":
        return {"jsonrpc": "2.0", "id": req_id, "result": {"tools": TOOLS_SPEC}}

    if method == "resources/list":
        return {"jsonrpc": "2.0", "id": req_id, "result": {"resources": []}}

    if method == "prompts/list":
        return {"jsonrpc": "2.0", "id": req_id, "result": {"prompts": []}}

    if method == "tools/call":
        params = req.get("params") or {}
        tool_name = str(params.get("name", ""))
        tool_args = params.get("arguments") or {}
        try:
            text_out = _dispatch_tool(tool_name, tool_args)
            return {
                "jsonrpc": "2.0",
                "id": req_id,
                "result": {"content": [{"type": "text", "text": text_out}], "isError": False},
            }
        except Exception as exc:
            err_detail = f"Tool '{tool_name}' error: {exc}\n{traceback.format_exc(limit=3)}"
            return {
                "jsonrpc": "2.0",
                "id": req_id,
                "result": {"content": [{"type": "text", "text": err_detail}], "isError": True},
            }

    return {
        "jsonrpc": "2.0",
        "id": req_id,
        "error": {"code": -32601, "message": f"Method not found: {method}"},
    }


def main() -> int:
    for stream in (sys.stdin, sys.stdout, sys.stderr):
        if hasattr(stream, "reconfigure"):
            try:
                stream.reconfigure(encoding="utf-8")
            except Exception:
                pass

    for raw_line in sys.stdin:
        line = raw_line.strip()
        if not line:
            continue
        try:
            req = json.loads(line)
        except json.JSONDecodeError:
            continue
        resp = handle_rpc_message(req)
        if resp is not None:
            _send(resp)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
