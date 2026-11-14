#!/usr/bin/env python3
"""Zero-Dependency Model Context Protocol (MCP) Stdio Server (`sqo-engine` v7.0).

Exposes 20 native, token-saving engineering & code-intelligence tools directly to
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
SERVER_VERSION = "7.0.0"

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
