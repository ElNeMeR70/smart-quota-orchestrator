#!/usr/bin/env python3
"""Comprehensive v3.0 test suite (18 tests covering MCP Server, PreToolUse Hook, BM25, Memory Vault, Blast Radius & all CLI engines)."""

from __future__ import annotations

import datetime as dt
import importlib.util
import json
import subprocess
import sys
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

handoff = _load_module("build_handoff_brief", "skills/context-compactor/scripts/build_handoff_brief.py")
outline_mod = _load_module("smart_outline", "skills/context-compactor/scripts/smart_outline.py")
pack_mod = _load_module("pack_context_bundle", "skills/context-compactor/scripts/pack_context_bundle.py")
diff_mod = _load_module("compress_git_diff", "skills/context-compactor/scripts/compress_git_diff.py")
denoise_mod = _load_module("compact_command_output", "skills/context-compactor/scripts/compact_command_output.py")
ignore_mod = _load_module("generate_agent_ignore", "skills/context-compactor/scripts/generate_agent_ignore.py")

bm25_mod = _load_module("search_code_bm25", "skills/semantic-code-navigator/scripts/search_code_bm25.py")
blast_mod = _load_module("analyze_blast_radius", "skills/semantic-code-navigator/scripts/analyze_blast_radius.py")
mem_mod = _load_module("memory_vault", "skills/project-memory-vault/scripts/memory_vault.py")
scrub_mod = _load_module("scrub_secrets", "skills/project-memory-vault/scripts/scrub_secrets.py")

slice_mod = _load_module("partition_parallel_slices", "skills/parallel-slice-architect/scripts/partition_parallel_slices.py")
tax_mod = _load_module("optimize_prompt_rules", "skills/prompt-tax-profiler/scripts/optimize_prompt_rules.py")

mcp_mod = _load_module("mcp_server", "mcp_server.py")
hook_mod = _load_module("token_shield_hook", "hooks/token_shield_hook.py")


class SmartQuotaEnterpriseV3Tests(unittest.TestCase):
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

    def test_12_pre_tool_use_token_shield_hook(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            lock = Path(tmp) / "package-lock.json"
            lock.write_text("x" * (80 * 1024), encoding="utf-8")

            blocked = hook_mod.evaluate_hook({
                "toolCall": {"name": "read_file", "args": {"Path": str(lock)}}
            })
            self.assertEqual(blocked["decision"], "deny")

            allowed_ranged = hook_mod.evaluate_hook({
                "toolCall": {"name": "read_file", "args": {"Path": str(lock), "StartLine": 1, "EndLine": 40}}
            })
            self.assertEqual(allowed_ranged["decision"], "allow")

            blocked_shell = hook_mod.evaluate_hook({
                "toolCall": {"name": "run_command", "args": {"CommandLine": "cat package-lock.json"}}
            })
            self.assertEqual(blocked_shell["decision"], "deny")

            allowed_shell = hook_mod.evaluate_hook({
                "toolCall": {"name": "run_command", "args": {"CommandLine": "cat package-lock.json | head -n 20"}}
            })
            self.assertEqual(allowed_shell["decision"], "allow")

    def test_13_mcp_stdio_server_json_rpc_protocol(self) -> None:
        init_resp = mcp_mod.handle_rpc_message({"jsonrpc": "2.0", "id": 1, "method": "initialize", "params": {"protocolVersion": "2025-03-26"}})
        assert init_resp is not None
        self.assertEqual(init_resp["result"]["serverInfo"]["name"], "sqo-engine")

        tools_resp = mcp_mod.handle_rpc_message({"jsonrpc": "2.0", "id": 2, "method": "tools/list"})
        assert tools_resp is not None
        self.assertEqual(len(tools_resp["result"]["tools"]), 10)

        call_resp = mcp_mod.handle_rpc_message({
            "jsonrpc": "2.0",
            "id": 3,
            "method": "tools/call",
            "params": {
                "name": "sqo_code_search",
                "arguments": {"workspace": str(REPO_ROOT / "skills"), "query": "analyze_pools", "top_k": 3},
            },
        })
        assert call_resp is not None
        self.assertFalse(call_resp["result"]["isError"])
        self.assertIn("parse_quota_pools.py", call_resp["result"]["content"][0]["text"])

    def test_14_compress_diff_and_denoise(self) -> None:
        sample_diff = (
            "diff --git a/yarn.lock b/yarn.lock\n--- a/yarn.lock\n+++ b/yarn.lock\n@@ -1 +1 @@\n-a\n+b\n"
            "diff --git a/src/api.ts b/src/api.ts\n--- a/src/api.ts\n+++ b/src/api.ts\n@@ -1 +1,2 @@\n+export const ok = true;\n"
        )
        d_res = diff_mod.compress_diff(sample_diff, max_tokens=400)
        self.assertEqual(len(d_res["skipped_lock_or_generated"]), 1)
        n_res = denoise_mod.denoise_output("PASS a\nPASS b\nFAIL c\nAssertionError: boom\nTests: 1 failed, 2 passed", exit_code=1)
        self.assertTrue(any("AssertionError" in x for x in n_res["diagnostic_lines"]))

    def test_15_manifests_v3_complete(self) -> None:
        plugin_data = json.loads((REPO_ROOT / "plugin.json").read_text(encoding="utf-8"))
        self.assertEqual(plugin_data["version"], "3.0.0")
        tax = tax_mod.profile_workspace(REPO_ROOT / "skills")
        self.assertEqual(len(tax["skills"]), 6)
        for ag in ("quota-planner.md", "token-auditor.md", "codebase-scout.md"):
            self.assertTrue((REPO_ROOT / "agents" / ag).is_file())
        self.assertTrue((REPO_ROOT / "mcp_config.json").is_file())
        self.assertTrue((REPO_ROOT / "hooks.json").is_file())


if __name__ == "__main__":
    unittest.main()
