#!/usr/bin/env python3
"""Comprehensive v4.0.0 test suite (22 tests covering the 3-Stage Stateful Lifecycle Engine,
14 Native MCP Tools, Incremental SQLite Code Graph & Route Mapper, 1-Turn Stack-Trace Pinpointer,
KV-Cache Prefix Stability Auditor, 5-IDE Synchronizer, BM25 Search, Blast Radius, Memory Vault & CLI)."""

from __future__ import annotations

import datetime as dt
import importlib.util
import json
import tempfile
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent


def _load_module(name: str, rel_path: str):
    target = REPO_ROOT / rel_path
    spec = importlib.util.spec_from_file_location(name, target)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


parse_quota = _load_module("parse_quota_pools", "skills/smart-quota-orchestrator/scripts/parse_quota_pools.py")
complexity = _load_module("analyze_task_complexity", "skills/smart-quota-orchestrator/scripts/analyze_task_complexity.py")
simulate_mod = _load_module("simulate_workflow_cost", "skills/smart-quota-orchestrator/scripts/simulate_workflow_cost.py")
audit_burn = _load_module("audit_session_burn", "skills/smart-quota-orchestrator/scripts/audit_session_burn.py")
dashboard_mod = _load_module("generate_html_dashboard", "skills/smart-quota-orchestrator/scripts/generate_html_dashboard.py")
bench_mod = _load_module("benchmark_suite", "skills/smart-quota-orchestrator/scripts/benchmark_suite.py")
sync_ide_mod = _load_module("sync_ide_configs", "skills/smart-quota-orchestrator/scripts/sync_ide_configs.py")

handoff = _load_module("build_handoff_brief", "skills/context-compactor/scripts/build_handoff_brief.py")
outline_mod = _load_module("smart_outline", "skills/context-compactor/scripts/smart_outline.py")
pack_mod = _load_module("pack_context_bundle", "skills/context-compactor/scripts/pack_context_bundle.py")
diff_mod = _load_module("compress_git_diff", "skills/context-compactor/scripts/compress_git_diff.py")
denoise_mod = _load_module("compact_command_output", "skills/context-compactor/scripts/compact_command_output.py")
ignore_mod = _load_module("generate_agent_ignore", "skills/context-compactor/scripts/generate_agent_ignore.py")

bm25_mod = _load_module("search_code_bm25", "skills/semantic-code-navigator/scripts/search_code_bm25.py")
blast_mod = _load_module("analyze_blast_radius", "skills/semantic-code-navigator/scripts/analyze_blast_radius.py")
graph_mod = _load_module("code_graph", "skills/semantic-code-navigator/scripts/code_graph.py")
pinpoint_mod = _load_module("pinpoint_stacktrace", "skills/semantic-code-navigator/scripts/pinpoint_stacktrace.py")

mem_mod = _load_module("memory_vault", "skills/project-memory-vault/scripts/memory_vault.py")
scrub_mod = _load_module("scrub_secrets", "skills/project-memory-vault/scripts/scrub_secrets.py")

slice_mod = _load_module("partition_parallel_slices", "skills/parallel-slice-architect/scripts/partition_parallel_slices.py")
tax_mod = _load_module("optimize_prompt_rules", "skills/prompt-tax-profiler/scripts/optimize_prompt_rules.py")
cache_mod = _load_module("audit_cache_stability", "skills/prompt-tax-profiler/scripts/audit_cache_stability.py")

mcp_mod = _load_module("mcp_server", "mcp_server.py")
hook_mod = _load_module("token_shield_hook", "hooks/token_shield_hook.py")


class SmartQuotaAutonomousOSV4Tests(unittest.TestCase):
    def test_01_parse_quota_pools(self) -> None:
        payload = {
            "models": ["gemini-4-carbon-medium", "gemini-pro-orchestrator", "claude-sonnet-4-6"],
            "display_names": {
                "gemini-4-carbon-medium": "Gemini 4 Carbon (Medium)",
                "gemini-pro-orchestrator": "Orchestrator (Carbon)",
                "claude-sonnet-4-6": "Claude Sonnet 4.6 (Thinking)",
            },
            "quotas": {
                "gemini-4-carbon-medium": {"quota_remaining": "36%", "quota_resets": "2026-11-14T06:00:00Z"},
                "gemini-pro-orchestrator": {"quota_remaining": "36%", "quota_resets": "2026-11-14T06:00:00Z"},
                "claude-sonnet-4-6": {"quota_remaining": "100%", "quota_resets": "2026-11-14T09:00:00Z"},
            },
        }
        now = dt.datetime(2026, 11, 14, 4, 0, 0, tzinfo=dt.timezone.utc)
        rep = parse_quota.analyze_pools(payload, now_utc=now)
        self.assertEqual(rep["pool_count"], 2)
        self.assertEqual(rep["pools"][0]["health"], "CONSERVE")

    def test_02_analyze_task_complexity(self) -> None:
        res = complexity.evaluate_task(REPO_ROOT / "skills", "Audit all files for auth jwt secret leaks and stripe billing", [])
        self.assertIn("security_auth", res["risk_domains"])
        self.assertIn("payments_billing", res["risk_domains"])

    def test_03_simulate_workflow_cost(self) -> None:
        sim = simulate_mod.simulate(files=15, avg_loc=250, turns=18)
        self.assertGreater(max(s["quota_savings_vs_carbon_high_pct"] for s in sim["strategies"]), 50.0)

    def test_04_audit_session_burn(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            t_path = Path(tmp) / "transcript.jsonl"
            steps = [
                {"step_index": 1, "status": "DONE", "tool_calls": [{"name": "read_file", "arguments": {"Path": "/a.py"}}]},
                {"step_index": 2, "status": "DONE", "tool_calls": [{"name": "read_file", "arguments": {"Path": "/a.py"}}]},
            ]
            t_path.write_text("\n".join(json.dumps(s) for s in steps), encoding="utf-8")
            rep = audit_burn.audit_transcript(t_path)
            self.assertEqual(rep["redundant_file_reads"].get("/a.py"), 1)

    def test_05_smart_outline_and_symbol_extraction(self) -> None:
        target = REPO_ROOT / "skills" / "smart-quota-orchestrator" / "scripts" / "parse_quota_pools.py"
        outline = outline_mod.build_outline(target)
        sym = outline_mod.extract_symbol_source(target, outline, "analyze_pools")
        self.assertIsNotNone(sym)

    def test_06_adaptive_context_packer(self) -> None:
        pack = pack_mod.pack_context(REPO_ROOT / "skills", [], ["parse_quota_pools.py"], max_tokens=2200)
        self.assertLessEqual(pack["packed_approx_tokens"], 2200)
        self.assertGreater(pack["token_savings_pct"], 50.0)

    def test_07_bm25_code_search_engine(self) -> None:
        res = bm25_mod.search_workspace(REPO_ROOT / "skills", "analyze_pools safe_burn_pct_per_hour", top_k=4)
        self.assertGreaterEqual(len(res["results"]), 1)
        self.assertIn("parse_quota_pools.py", res["results"][0]["file"])
        self.assertGreater(res["token_savings_pct"], 80.0)

    def test_08_blast_radius_and_minimal_test_selector(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            ws = Path(tmp)
            (ws / "src").mkdir()
            (ws / "tests").mkdir()
            (ws / "src" / "token.ts").write_text("export const sign = () => 'ok';\n", encoding="utf-8")
            (ws / "src" / "auth.ts").write_text("import { sign } from './token';\nexport const login = () => sign();\n", encoding="utf-8")
            (ws / "tests" / "auth.spec.ts").write_text("import { login } from '../src/auth';\n", encoding="utf-8")
            (ws / "src" / "unrelated.ts").write_text("export const ping = () => 1;\n", encoding="utf-8")

            rep = blast_mod.compute_blast_radius(ws, ["src/token.ts"])
            self.assertIn("src/auth.ts", rep["direct_dependents"])
            self.assertIn("tests/auth.spec.ts", rep["transitive_dependents"])
            self.assertIn("tests/auth.spec.ts", rep["affected_test_files"])

    def test_09_persistent_memory_vault_fts5(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            db = Path(tmp) / "vault.db"
            saved = mem_mod.remember_fact(db, "auth", "Stripe raw body requirement", "Keep raw Buffer before express.json()", ["src/app.ts"])
            hits = mem_mod.recall_facts(db, "Stripe express buffer")
            self.assertEqual(len(hits), 1)
            self.assertEqual(hits[0]["id"], saved["id"])
            self.assertTrue(mem_mod.forget_fact(db, saved["id"]))
            self.assertEqual(len(mem_mod.list_facts(db)), 0)

    def test_10_secret_redactor_and_scanner(self) -> None:
        fake_gh = "ghp_" + ("A1b2C3d4E5" * 4)
        fake_uri = "postgres://admin:superSecretPass123@db.internal:5432/prod"
        res = scrub_mod.scrub_text(f"TOKEN={fake_gh}\nDB={fake_uri}")
        self.assertEqual(res["redacted_total"], 2)
        self.assertNotIn("superSecretPass123", res["scrubbed_text"])
        self.assertIn("<REDACTED_GITHUB_PAT_1>", res["scrubbed_text"])

    def test_11_empirical_benchmark_suite(self) -> None:
        rep = bench_mod.run_live_benchmark(REPO_ROOT / "skills", REPO_ROOT / "skills")
        self.assertEqual(len(rep["benchmarks"]), 4)
        self.assertGreater(rep["average_token_reduction_pct"], 70.0)

    def test_12_hook_lockfile_and_shell_shield(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            lock = Path(tmp) / "package-lock.json"
            lock.write_text("x" * (80 * 1024), encoding="utf-8")

            blocked = hook_mod.evaluate_hook({
                "hookEventName": "PreToolUse",
                "toolCall": {"name": "read_file", "args": {"Path": str(lock)}},
            })
            self.assertEqual(blocked["decision"], "deny")

            allowed_ranged = hook_mod.evaluate_hook({
                "hookEventName": "PreToolUse",
                "toolCall": {"name": "read_file", "args": {"Path": str(lock), "StartLine": 1, "EndLine": 40}},
            })
            self.assertEqual(allowed_ranged["decision"], "allow")

            blocked_shell = hook_mod.evaluate_hook({
                "hookEventName": "PreToolUse",
                "toolCall": {"name": "run_command", "args": {"CommandLine": "cat package-lock.json"}},
            })
            self.assertEqual(blocked_shell["decision"], "deny")

            allowed_shell = hook_mod.evaluate_hook({
                "hookEventName": "PreToolUse",
                "toolCall": {"name": "run_command", "args": {"CommandLine": "cat package-lock.json | head -n 20"}},
            })
            self.assertEqual(allowed_shell["decision"], "allow")

    def test_13_stateful_hook_dedup_autoclamp_loopbreaker_and_sessionstart(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            ws = Path(tmp) / "ws"
            state_dir = Path(tmp) / "state"
            ws.mkdir()

            # A) SessionStart warm memory injection
            mem_db = ws / ".sqo" / "memory.db"
            mem_mod.remember_fact(mem_db, "arch", "Billing webhook port", "Runs on port 8081", ["src/webhook.py"])
            start_out = hook_mod.evaluate_hook({"hookEventName": "SessionStart", "cwd": str(ws)}, state_root=state_dir)
            self.assertIn("injectSteps", start_out)
            self.assertIn("Billing webhook port", start_out["injectSteps"][0]["systemMessage"]["systemMessage"])

            # B) Duplicate-read deduplication + edit_file unlock
            src = ws / "service.py"
            src.write_text("def run():\n    return 42\n", encoding="utf-8")
            conv_id = "conv-v4-test"

            r1 = hook_mod.evaluate_hook(
                {"hookEventName": "PreToolUse", "conversationId": conv_id, "toolCall": {"name": "read_file", "args": {"Path": str(src)}}},
                state_root=state_dir,
            )
            self.assertEqual(r1["decision"], "allow")
            hook_mod.evaluate_hook(
                {"hookEventName": "PostToolUse", "conversationId": conv_id, "stepIdx": 3, "toolCall": {"name": "read_file", "args": {"Path": str(src)}}},
                state_root=state_dir,
            )

            # Second identical unchanged read -> DENIED!
            r2 = hook_mod.evaluate_hook(
                {"hookEventName": "PreToolUse", "conversationId": conv_id, "toolCall": {"name": "read_file", "args": {"Path": str(src)}}},
                state_root=state_dir,
            )
            self.assertEqual(r2["decision"], "deny")
            self.assertIn("Deduplicator", r2["reason"])

            # Edit the file -> PostToolUse clears read lock -> allowed again!
            src.write_text("def run():\n    return 99\n", encoding="utf-8")
            hook_mod.evaluate_hook(
                {"hookEventName": "PostToolUse", "conversationId": conv_id, "toolCall": {"name": "edit_file", "args": {"Path": str(src)}}},
                state_root=state_dir,
            )
            r3 = hook_mod.evaluate_hook(
                {"hookEventName": "PreToolUse", "conversationId": conv_id, "toolCall": {"name": "read_file", "args": {"Path": str(src)}}},
                state_root=state_dir,
            )
            self.assertEqual(r3["decision"], "allow")

            # C) Auto-Clamp (`overwrite`) on giant source file (>55 KB & >1,200 lines)
            giant = ws / "monolith.py"
            giant.write_text(("def fn_x(): return '" + ("a" * 45) + "'\n") * 1350, encoding="utf-8")
            clamped = hook_mod.evaluate_hook(
                {"hookEventName": "PreToolUse", "conversationId": "conv-clamp", "toolCall": {"name": "read_file", "args": {"Path": str(giant)}}},
                state_root=state_dir,
            )
            self.assertEqual(clamped["decision"], "allow")
            self.assertEqual(clamped.get("overwrite"), {"StartLine": 1, "EndLine": 280})

            # D) Blind Retry-Loop Breaker (3rd consecutive identical failing command denied)
            bad_cmd = {"name": "run_command", "args": {"CommandLine": "pytest tests/broken.py"}}
            for _ in range(2):
                hook_mod.evaluate_hook(
                    {"hookEventName": "PostToolUse", "conversationId": conv_id, "error": "Exit code 1", "toolCall": bad_cmd},
                    state_root=state_dir,
                )
            third_try = hook_mod.evaluate_hook(
                {"hookEventName": "PreToolUse", "conversationId": conv_id, "toolCall": bad_cmd},
                state_root=state_dir,
            )
            self.assertEqual(third_try["decision"], "deny")
            self.assertIn("Loop-Breaker", third_try["reason"])

    def test_14_incremental_code_graph_and_route_mapper(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            ws = Path(tmp)
            (ws / "src").mkdir()
            (ws / "src" / "db.py").write_text(
                "def query(x):\n    if x and (x > 1 or x < 0):\n        return x\n    return 0\n",
                encoding="utf-8",
            )
            (ws / "src" / "api.py").write_text(
                "from src.db import query\n\n@app.post('/api/v1/checkout')\ndef checkout():\n    return query(2)\n",
                encoding="utf-8",
            )
            (ws / "src" / "orphan_helper.py").write_text("def unused():\n    return True\n", encoding="utf-8")

            hot1 = graph_mod.analyze_hotspots(ws, top_k=5)
            self.assertEqual(hot1["sync_stats"]["reindexed_modified_files"], 3)
            self.assertEqual(hot1["top_hotspots"][0]["file"], "src/db.py")
            self.assertIn("src/orphan_helper.py", hot1["potential_unreferenced_modules"])

            # Second run should hit 100% incremental SQLite cache!
            routes = graph_mod.extract_all_routes(ws)
            self.assertEqual(routes["sync_stats"]["cached_unchanged_files"], 3)
            self.assertEqual(routes["sync_stats"]["reindexed_modified_files"], 0)
            self.assertEqual(routes["route_count"], 1)
            self.assertEqual(routes["routes"][0]["path"], "/api/v1/checkout")
            self.assertEqual(routes["routes"][0]["method"], "POST")

    def test_15_stacktrace_pinpointer(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            ws = Path(tmp)
            (ws / "app").mkdir()
            lines = [f"line_{i} = {i}" for i in range(1, 40)]
            lines[19] = "result = 1 / 0  # boom"
            (ws / "app" / "billing.py").write_text("\n".join(lines) + "\n", encoding="utf-8")

            trace = (
                'Traceback (most recent call last):\n'
                '  File "/usr/lib/python3.12/site-packages/starlette/routing.py", line 72, in app\n'
                f'  File "{ws / "app" / "billing.py"}", line 20, in charge\n'
                'ZeroDivisionError: division by zero\n'
            )
            rep = pinpoint_mod.pinpoint_trace(ws, trace, radius=4)
            self.assertEqual(rep["frames_extracted"], 1)
            self.assertEqual(rep["frames"][0]["file"], "app/billing.py")
            self.assertEqual(rep["frames"][0]["crash_line"], 20)
            self.assertIn(">>   20 | result = 1 / 0  # boom", rep["frames"][0]["snippet"])

    def test_16_kv_cache_prefix_stability_auditor(self) -> None:
        # 1. Audit our own plugin skills + hooks (verify 100/100 score!)
        with tempfile.TemporaryDirectory() as clean_tmp:
            cws = Path(clean_tmp)
            (cws / "hooks.json").write_text((REPO_ROOT / "hooks.json").read_text(encoding="utf-8"), encoding="utf-8")
            (cws / "hooks").mkdir()
            (cws / "hooks" / "token_shield_hook.py").write_text(
                (REPO_ROOT / "hooks" / "token_shield_hook.py").read_text(encoding="utf-8"),
                encoding="utf-8",
            )
            clean_rep = cache_mod.audit_cache_stability(cws)
            self.assertEqual(clean_rep["cache_stability_score"], 100)

        # 2. Detect PreInvocation + datetime.now() cache-busting anti-pattern
        with tempfile.TemporaryDirectory() as bad_tmp:
            bws = Path(bad_tmp)
            (bws / "hooks.json").write_text('{"hooks": {"PreInvocation": []}}', encoding="utf-8")
            (bws / "hooks").mkdir()
            (bws / "hooks" / "bad_hook.py").write_text(
                "import datetime\nmsg = {'injectSteps': str(datetime.now())}\n",
                encoding="utf-8",
            )
            bad_rep = cache_mod.audit_cache_stability(bws)
            self.assertLess(bad_rep["cache_stability_score"], 70)
            self.assertTrue(bad_rep["has_per_turn_pre_invocation"])

    def test_17_cross_ide_config_synchronizer(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            ws = Path(tmp)
            res = sync_ide_mod.sync_workspace_ides(ws, REPO_ROOT, ["all"], dry_run=False)
            self.assertEqual(len(res["synced_files"]), 7)
            self.assertTrue((ws / ".agentignore").is_file())
            self.assertTrue((ws / ".cursor" / "mcp.json").is_file())
            self.assertTrue((ws / ".mcp.json").is_file())
            self.assertTrue((ws / ".vscode" / "mcp.json").is_file())
            vscode_cfg = json.loads((ws / ".vscode" / "mcp.json").read_text(encoding="utf-8"))
            self.assertIn("sqo-engine", vscode_cfg["servers"])

    def test_18_mcp_stdio_server_14_tools(self) -> None:
        init_resp = mcp_mod.handle_rpc_message({"jsonrpc": "2.0", "id": 1, "method": "initialize", "params": {"protocolVersion": "2025-03-26"}})
        assert init_resp is not None
        self.assertEqual(init_resp["result"]["serverInfo"]["version"], "4.0.0")

        tools_resp = mcp_mod.handle_rpc_message({"jsonrpc": "2.0", "id": 2, "method": "tools/list"})
        assert tools_resp is not None
        tool_names = {t["name"] for t in tools_resp["result"]["tools"]}
        self.assertEqual(len(tool_names), 14)
        for expected in ("sqo_pinpoint_error", "sqo_code_hotspots", "sqo_api_routes", "sqo_cache_audit"):
            self.assertIn(expected, tool_names)

        call_resp = mcp_mod.handle_rpc_message({
            "jsonrpc": "2.0",
            "id": 3,
            "method": "tools/call",
            "params": {
                "name": "sqo_code_hotspots",
                "arguments": {"workspace": str(REPO_ROOT / "skills"), "top_k": 3},
            },
        })
        assert call_resp is not None
        self.assertFalse(call_resp["result"]["isError"])
        self.assertIn("Hotspot", call_resp["result"]["content"][0]["text"])

    def test_19_compress_diff_and_denoise(self) -> None:
        sample_diff = (
            "diff --git a/yarn.lock b/yarn.lock\n--- a/yarn.lock\n+++ b/yarn.lock\n@@ -1 +1 @@\n-a\n+b\n"
            "diff --git a/src/api.ts b/src/api.ts\n--- a/src/api.ts\n+++ b/src/api.ts\n@@ -1 +1,2 @@\n+export const ok = true;\n"
        )
        d_res = diff_mod.compress_diff(sample_diff, max_tokens=400)
        self.assertEqual(len(d_res["skipped_lock_or_generated"]), 1)
        n_res = denoise_mod.denoise_output("PASS a\nPASS b\nFAIL c\nAssertionError: boom\nTests: 1 failed, 2 passed", exit_code=1)
        self.assertTrue(any("AssertionError" in x for x in n_res["diagnostic_lines"]))

    def test_20_parallel_dependency_slices(self) -> None:
        rep = slice_mod.partition_workspace(REPO_ROOT / "skills", [], max_workers=3)
        self.assertGreaterEqual(rep["total_source_files"], 15)
        self.assertTrue(rep["collision_free_guarantee"])

    def test_21_handoff_brief_and_html_dashboard(self) -> None:
        brief = handoff.build_brief(REPO_ROOT / "skills", "Ship v4.0", ["Push tag"])
        self.assertEqual(brief["goal"], "Ship v4.0")
        html_doc = dashboard_mod.build_dashboard_html(REPO_ROOT / "skills", REPO_ROOT / "skills")
        self.assertIn("Telemetry Center", html_doc)

    def test_22_manifests_v4_complete(self) -> None:
        for mf in ("plugin.json", ".claude-plugin/plugin.json", "gemini-extension.json"):
            data = json.loads((REPO_ROOT / mf).read_text(encoding="utf-8"))
            self.assertEqual(data["version"], "4.0.0")
        self.assertTrue((REPO_ROOT / "pyproject.toml").is_file())
        tax = tax_mod.profile_workspace(REPO_ROOT / "skills")
        self.assertEqual(len(tax["skills"]), 6)


if __name__ == "__main__":
    unittest.main()
