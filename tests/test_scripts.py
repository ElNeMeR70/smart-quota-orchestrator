#!/usr/bin/env python3
"""Comprehensive v5.0.0 test suite (26 tests covering the 3-Stage Stateful Lifecycle Engine,
Live $USD & Token ROI Ledger, Multi-Modal Vision/PDF Budgeter, Git Pre-Commit Guard,
16 Native MCP Tools, Incremental SQLite Code Graph & Route Mapper, 1-Turn Stack-Trace Pinpointer,
KV-Cache Prefix Stability Auditor, 5-IDE Synchronizer, Visual Assets & Bilingual Playbooks)."""

from __future__ import annotations

import datetime as dt
import importlib.util
import json
import struct
import tempfile
import unittest
import zlib
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
roi_mod = _load_module("roi_ledger", "skills/smart-quota-orchestrator/scripts/roi_ledger.py")
git_guard_mod = _load_module("install_git_guard", "skills/smart-quota-orchestrator/scripts/install_git_guard.py")
live_srv_mod = _load_module("live_server", "skills/smart-quota-orchestrator/scripts/live_server.py")
preset_mod = _load_module("init_workspace_preset", "skills/smart-quota-orchestrator/scripts/init_workspace_preset.py")
rot_mod = _load_module("check_context_rot", "skills/smart-quota-orchestrator/scripts/check_context_rot.py")
badge_mod = _load_module("generate_repo_badge", "skills/smart-quota-orchestrator/scripts/generate_repo_badge.py")
shadow_mod = _load_module("shadow_dry_run", "skills/smart-quota-orchestrator/scripts/shadow_dry_run.py")
tm_mod = _load_module("time_machine", "skills/smart-quota-orchestrator/scripts/time_machine.py")
ci_mod = _load_module("generate_ci_shield", "skills/smart-quota-orchestrator/scripts/generate_ci_shield.py")
share_mod = _load_module("cloud_share", "skills/smart-quota-orchestrator/scripts/cloud_share.py")
hive_mod = _load_module("hive_mind", "skills/project-memory-vault/scripts/hive_mind.py")
schema_mod = _load_module("distill_schema", "skills/context-compactor/scripts/distill_schema.py")
vdeps_mod = _load_module("verify_hallucinations", "skills/smart-quota-orchestrator/scripts/verify_hallucinations.py")
i18n_mod = _load_module("audit_i18n", "skills/context-compactor/scripts/audit_i18n.py")
memo_mod = _load_module("semantic_cache", "skills/smart-quota-orchestrator/scripts/semantic_cache.py")
contracts_mod = _load_module("extract_contracts", "skills/context-compactor/scripts/extract_contracts.py")
swarm_plan_mod = _load_module("plan_swarm", "skills/parallel-slice-architect/scripts/plan_swarm.py")
hub_mod = _load_module("cloud_hub", "skills/smart-quota-orchestrator/scripts/cloud_hub.py")

sym_mod = _load_module("edit_symbol", "skills/apex-spec-surgeon/scripts/edit_symbol.py")
spec_mod = _load_module("spec_engine", "skills/apex-spec-surgeon/scripts/spec_engine.py")
mgraph_mod = _load_module("memory_graph", "skills/project-memory-vault/scripts/memory_graph.py")
karp_mod = _load_module("verify_karpathy", "skills/apex-spec-surgeon/scripts/verify_karpathy.py")
sdk_mod = _load_module("sdk_radar", "skills/apex-spec-surgeon/scripts/sdk_radar.py")
sandbox_mod = _load_module("worktree_sandbox", "skills/apex-spec-surgeon/scripts/worktree_sandbox.py")

handoff = _load_module("build_handoff_brief", "skills/context-compactor/scripts/build_handoff_brief.py")
outline_mod = _load_module("smart_outline", "skills/context-compactor/scripts/smart_outline.py")
pack_mod = _load_module("pack_context_bundle", "skills/context-compactor/scripts/pack_context_bundle.py")
diff_mod = _load_module("compress_git_diff", "skills/context-compactor/scripts/compress_git_diff.py")
denoise_mod = _load_module("compact_command_output", "skills/context-compactor/scripts/compact_command_output.py")
ignore_mod = _load_module("generate_agent_ignore", "skills/context-compactor/scripts/generate_agent_ignore.py")
media_mod = _load_module("estimate_media_tokens", "skills/context-compactor/scripts/estimate_media_tokens.py")
prompt_comp_mod = _load_module("compress_prompt", "skills/context-compactor/scripts/compress_prompt.py")

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


def _make_minimal_png(width: int, height: int) -> bytes:
    ihdr = struct.pack(">IIBBBBB", width, height, 8, 2, 0, 0, 0)
    chunk = b"IHDR" + ihdr
    return b"\x89PNG\r\n\x1a\n" + struct.pack(">I", 13) + chunk + struct.pack(">I", zlib.crc32(chunk) & 0xFFFFFFFF)


class SmartQuotaAutonomousOSV5Tests(unittest.TestCase):
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

    def test_12_hook_lockfile_and_shell_shield_plus_roi_tracking(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            state_dir = Path(tmp) / "state"
            lock = Path(tmp) / "package-lock.json"
            lock.write_text("x" * (80 * 1024), encoding="utf-8")

            blocked = hook_mod.evaluate_hook(
                {"hookEventName": "PreToolUse", "toolCall": {"name": "read_file", "args": {"Path": str(lock)}}},
                state_root=state_dir,
            )
            self.assertEqual(blocked["decision"], "deny")

            # Verify automatic ROI ledger recording!
            roi_summary = roi_mod.summarize_roi(state_dir / "roi_ledger.db")
            self.assertEqual(roi_summary["total_interceptions"], 1)
            self.assertGreater(roi_summary["total_tokens_saved"], 15000)

    def test_13_stateful_hook_dedup_autoclamp_loopbreaker_and_sessionstart(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            ws = Path(tmp) / "ws"
            state_dir = Path(tmp) / "state"
            ws.mkdir()

            mem_db = ws / ".sqo" / "memory.db"
            mem_mod.remember_fact(mem_db, "arch", "Billing webhook port", "Runs on port 8081", ["src/webhook.py"])
            start_out = hook_mod.evaluate_hook({"hookEventName": "SessionStart", "cwd": str(ws)}, state_root=state_dir)
            self.assertIn("injectSteps", start_out)

            src = ws / "service.py"
            src.write_text("def run():\n    return 42\n", encoding="utf-8")
            conv_id = "conv-v5-test"

            r1 = hook_mod.evaluate_hook(
                {"hookEventName": "PreToolUse", "conversationId": conv_id, "toolCall": {"name": "read_file", "args": {"Path": str(src)}}},
                state_root=state_dir,
            )
            self.assertEqual(r1["decision"], "allow")
            hook_mod.evaluate_hook(
                {"hookEventName": "PostToolUse", "conversationId": conv_id, "stepIdx": 3, "toolCall": {"name": "read_file", "args": {"Path": str(src)}}},
                state_root=state_dir,
            )

            r2 = hook_mod.evaluate_hook(
                {"hookEventName": "PreToolUse", "conversationId": conv_id, "toolCall": {"name": "read_file", "args": {"Path": str(src)}}},
                state_root=state_dir,
            )
            self.assertEqual(r2["decision"], "deny")

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

            giant = ws / "monolith.py"
            giant.write_text(("def fn_x(): return '" + ("a" * 45) + "'\n") * 1350, encoding="utf-8")
            clamped = hook_mod.evaluate_hook(
                {"hookEventName": "PreToolUse", "conversationId": "conv-clamp", "toolCall": {"name": "read_file", "args": {"Path": str(giant)}}},
                state_root=state_dir,
            )
            self.assertEqual(clamped.get("overwrite"), {"StartLine": 1, "EndLine": 280})

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
            self.assertEqual(hot1["top_hotspots"][0]["file"], "src/db.py")
            routes = graph_mod.extract_all_routes(ws)
            self.assertEqual(routes["sync_stats"]["cached_unchanged_files"], 3)
            self.assertEqual(routes["route_count"], 1)

    def test_15_stacktrace_pinpointer(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            ws = Path(tmp)
            (ws / "app").mkdir()
            lines = [f"line_{i} = {i}" for i in range(1, 40)]
            lines[19] = "result = 1 / 0  # boom"
            (ws / "app" / "billing.py").write_text("\n".join(lines) + "\n", encoding="utf-8")
            trace = f'  File "{ws / "app" / "billing.py"}", line 20, in charge\nZeroDivisionError: division by zero\n'
            rep = pinpoint_mod.pinpoint_trace(ws, trace, radius=4)
            self.assertEqual(rep["frames_extracted"], 1)
            self.assertEqual(rep["frames"][0]["crash_line"], 20)

    def test_16_kv_cache_prefix_stability_auditor(self) -> None:
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

    def test_17_cross_ide_config_synchronizer(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            ws = Path(tmp)
            res = sync_ide_mod.sync_workspace_ides(ws, REPO_ROOT, ["all"], dry_run=False)
            self.assertEqual(len(res["synced_files"]), 7)
            self.assertTrue((ws / ".cursor" / "mcp.json").is_file())

    def test_18_mcp_stdio_server_38_tools(self) -> None:
        init_resp = mcp_mod.handle_rpc_message({"jsonrpc": "2.0", "id": 1, "method": "initialize", "params": {"protocolVersion": "2025-03-26"}})
        assert init_resp is not None
        self.assertEqual(init_resp["result"]["serverInfo"]["version"], "10.0.0")

        tools_resp = mcp_mod.handle_rpc_message({"jsonrpc": "2.0", "id": 2, "method": "tools/list"})
        assert tools_resp is not None
        tool_names = {t["name"] for t in tools_resp["result"]["tools"]}
        self.assertEqual(len(tool_names), 38)
        for expected in (
            "sqo_edit_symbol",
            "sqo_find_callers",
            "sqo_spec_engine",
            "sqo_memory_graph",
            "sqo_verify_work",
            "sqo_sdk_radar",
            "sqo_worktree_sandbox",
            "sqo_verify_deps",
            "sqo_i18n_audit",
            "sqo_memo_cache",
            "sqo_api_contracts",
            "sqo_swarm_plan",
            "sqo_cloud_hub",
            "sqo_hive_mind",
            "sqo_schema_distill",
            "sqo_shadow_check",
            "sqo_checkpoint",
        ):
            self.assertIn(expected, tool_names)

    def test_19_compress_diff_and_denoise(self) -> None:
        sample_diff = (
            "diff --git a/yarn.lock b/yarn.lock\n--- a/yarn.lock\n+++ b/yarn.lock\n@@ -1 +1 @@\n-a\n+b\n"
            "diff --git a/src/api.ts b/src/api.ts\n--- a/src/api.ts\n+++ b/src/api.ts\n@@ -1 +1,2 @@\n+export const ok = true;\n"
        )
        d_res = diff_mod.compress_diff(sample_diff, max_tokens=400)
        self.assertEqual(len(d_res["skipped_lock_or_generated"]), 1)
        n_res = denoise_mod.denoise_output("PASS a\nFAIL c\nAssertionError: boom\nTests: 1 failed, 1 passed", exit_code=1)
        self.assertTrue(any("AssertionError" in x for x in n_res["diagnostic_lines"]))

    def test_20_parallel_dependency_slices(self) -> None:
        rep = slice_mod.partition_workspace(REPO_ROOT / "skills", [], max_workers=3)
        self.assertGreaterEqual(rep["total_source_files"], 15)
        self.assertTrue(rep["collision_free_guarantee"])

    def test_21_handoff_brief_and_html_dashboard(self) -> None:
        brief = handoff.build_brief(REPO_ROOT / "skills", "Ship v5.0", ["Push tag"])
        self.assertEqual(brief["goal"], "Ship v5.0")
        html_doc = dashboard_mod.build_dashboard_html(REPO_ROOT / "skills", REPO_ROOT / "skills")
        self.assertIn("Telemetry Center", html_doc)

    def test_22_roi_ledger_usd_calculations(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            db = Path(tmp) / "roi.db"
            roi_mod.record_saving("Token-Bomb Blocker", 500_000, target="package-lock.json", db_path=db)
            roi_mod.record_saving("Duplicate-Read Deduplicator", 500_000, target="app.ts", db_path=db)
            rep = roi_mod.summarize_roi(db)
            self.assertEqual(rep["total_tokens_saved"], 1_000_000)
            self.assertAlmostEqual(rep["usd_equivalents"]["frontier_opus_pro"]["saved_usd"], 15.0, places=2)
            self.assertAlmostEqual(rep["usd_equivalents"]["balanced_sonnet_carbon"]["saved_usd"], 3.0, places=2)

    def test_23_multimodal_media_token_estimator(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            ws = Path(tmp)
            uhd_png = ws / "screenshot_4k.png"
            uhd_png.write_bytes(_make_minimal_png(3840, 2160))
            pdf = ws / "spec.pdf"
            pdf.write_bytes(b"%PDF-1.7\n1 0 obj << /Type /Pages /Count 20 >> endobj\n")

            rep = media_mod.scan_media_paths([], ws)
            self.assertEqual(rep["scanned_count"], 2)
            self.assertEqual(rep["oversized_count"], 2)
            self.assertGreater(rep["total_gemini_tokens"], 5000)

    def test_24_git_precommit_guard_installer(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            ws = Path(tmp)
            (ws / ".git").mkdir()
            res = git_guard_mod.install_guard(ws, REPO_ROOT)
            self.assertTrue(res["installed"])
            self.assertTrue((ws / ".git" / "hooks" / "pre-commit").is_file())

    def test_25_visual_assets_landing_page_and_bilingual_playbooks_present(self) -> None:
        for asset in ("logo.svg", "hero-banner.jpg", "architecture-v5.svg", "benchmark-comparison.svg", "shield-lifecycle.svg", "terminal-roi-preview.svg"):
            self.assertTrue((REPO_ROOT / "assets" / asset).is_file(), f"Missing visual asset: {asset}")
        for doc in ("README.md", "README.ar.md", "docs/index.html", "docs/LAUNCH_KIT.md", "docs/PLAYBOOK_EN.md", "docs/PLAYBOOK_AR.md", "smithery.yaml", "glama.json"):
            self.assertTrue((REPO_ROOT / doc).is_file(), f"Missing documentation/registry file: {doc}")

    def test_26_smart_framework_preset_auto_bootstrapper(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            ws = Path(tmp)
            (ws / "pubspec.yaml").write_text("name: demo_app\n", encoding="utf-8")
            (ws / ".git").mkdir()
            rep = preset_mod.initialize_workspace(ws, preset="auto", with_git_guard=True)
            self.assertEqual(rep["detected_preset"], "flutter")
            self.assertGreaterEqual(rep["seeded_memories"], 2)
            self.assertTrue(rep["git_guard_installed"])
            agent_ig = (ws / ".agentignore").read_text(encoding="utf-8")
            self.assertIn("*.g.dart", agent_ig)

    def test_27_context_rot_early_warning_monitor(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            ws = Path(tmp)
            t_file = ws / "transcript.jsonl"
            big_steps = [{"step_index": i, "tool_calls": [{"name": "read_file"}], "content": "x" * 2400} for i in range(60)]
            t_file.write_text("\n".join(json.dumps(s) for s in big_steps), encoding="utf-8")
            rep = rot_mod.evaluate_context_health(REPO_ROOT / "skills", transcript_path=t_file, goal="Ship v6.0")
            self.assertGreaterEqual(rep["context_rot_score"], 50)
            self.assertIn("Ship v6.0", rep["ready_handoff_brief"])

    def test_28_live_localhost_web_command_center_api(self) -> None:
        import threading
        import urllib.request
        from http.server import ThreadingHTTPServer

        with tempfile.TemporaryDirectory() as tmp:
            ws = Path(tmp)
            (ws / "app.py").write_text("@app.get('/health')\ndef health():\n    return {'ok': True}\n", encoding="utf-8")
            srv = ThreadingHTTPServer(("127.0.0.1", 0), live_srv_mod.make_handler(ws))
            port = srv.server_address[1]
            t = threading.Thread(target=srv.serve_forever, daemon=True)
            t.start()
            try:
                with urllib.request.urlopen(f"http://127.0.0.1:{port}/api/overview", timeout=4) as resp:
                    data = json.loads(resp.read().decode("utf-8"))
                self.assertEqual(data["version"], "10.0.0")
                self.assertEqual(data["routes"][0]["path"], "/health")

                req = urllib.request.Request(
                    f"http://127.0.0.1:{port}/api/memories",
                    data=json.dumps({"category": "arch", "title": "Port info", "detail": "8080"}).encode("utf-8"),
                    headers={"Content-Type": "application/json"},
                    method="POST",
                )
                with urllib.request.urlopen(req, timeout=4) as post_resp:
                    saved = json.loads(post_resp.read().decode("utf-8"))
                self.assertTrue(saved["ok"])
            finally:
                srv.shutdown()
                srv.server_close()

    def test_29_manifests_v10_complete(self) -> None:
        for mf in ("plugin.json", ".claude-plugin/plugin.json", "gemini-extension.json", "glama.json", "package.json", "vscode-extension/package.json"):
            data = json.loads((REPO_ROOT / mf).read_text(encoding="utf-8"))
            self.assertEqual(data["version"], "10.0.0")
        self.assertTrue((REPO_ROOT / "pyproject.toml").is_file())
        self.assertTrue((REPO_ROOT / "bin" / "sqo.js").is_file())
        self.assertTrue((REPO_ROOT / "vscode-extension" / "extension.js").is_file())
        self.assertTrue((REPO_ROOT / "docs" / "api" / "telemetry.php").is_file())
        self.assertTrue((REPO_ROOT / "docs" / "api" / "card.php").is_file())
        self.assertTrue((REPO_ROOT / "docs" / "api" / "presets.php").is_file())
        self.assertTrue((REPO_ROOT / "docs" / "apex-skill.md").is_file())
        tax = tax_mod.profile_workspace(REPO_ROOT / "skills")
        self.assertEqual(len(tax["skills"]), 7)

    def test_30_prompt_json_and_log_compressor(self) -> None:
        big_items = [{"id": i, "email": f"u{i}@test.dev", "status": "ACTIVE"} for i in range(40)]
        noisy = (
            "Authorization: Bearer sk-proj-ABCDEFGHIJKLMNOPQRSTUVWXYZ123456\n"
            + "\n".join(["[WARN] Redis socket retry"] * 12)
            + "\n```json\n"
            + json.dumps(big_items, indent=2)
            + "\n```\n"
        )
        res = prompt_comp_mod.compress_raw_prompt(noisy)
        self.assertGreater(res["savings_pct"], 60.0)
        self.assertGreaterEqual(res["secrets_redacted"], 1)
        self.assertIn("Repeated", res["compressed_text"])
        self.assertNotIn("sk-proj-ABCDEFGH", res["compressed_text"])

    def test_31_dynamic_svg_repo_badge_generator(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            out_svg = Path(tmp) / "badge.svg"
            svg_txt, meta = badge_mod.build_badge_svg(REPO_ROOT / "skills")
            out_svg.write_text(svg_txt, encoding="utf-8")
            self.assertTrue(out_svg.is_file())
            self.assertIn("<svg", svg_txt)
            self.assertIn("Smart Quota", svg_txt)
            self.assertGreater(meta["reduction_pct"], 50.0)

    def test_32_cross_repo_hive_mind_federation(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            tpath = Path(tmp)
            hive_db = tpath / "hive.db"
            repo_a = tpath / "app_a"
            repo_b = tpath / "app_b"
            repo_a.mkdir()
            repo_b.mkdir()
            (repo_a / "pubspec.yaml").write_text("name: a\n", encoding="utf-8")
            (repo_b / "pubspec.yaml").write_text("name: b\n", encoding="utf-8")

            r1 = hive_mod.store_hive_lesson(hive_db, "flutter", "gotcha", "Gradle JVM Heap", "Use -Xmx4G and sk-proj-SECRET12345678901234567890", source_repo="app_a")
            self.assertFalse(r1["deduplicated"])
            hits = hive_mod.recall_hive(hive_db, query="Gradle Heap", stack="flutter")
            self.assertEqual(len(hits), 1)
            self.assertNotIn("SECRET123456", hits[0]["detail"])

            inj = hive_mod.inject_into_workspace(repo_b, hive_db, stack="auto")
            self.assertEqual(inj["injected_count"], 1)

    def test_33_universal_6_stack_schema_distiller(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            ws = Path(tmp)
            (ws / "schema.sql").write_text(
                "CREATE TABLE users (id INT PRIMARY KEY, email VARCHAR(255));\n"
                "CREATE TABLE orders (id INT PRIMARY KEY, user_id INT REFERENCES users(id), total DECIMAL(10,2));\n"
                + ("-- migration comment padding\n" * 80),
                encoding="utf-8",
            )
            (ws / "schema.prisma").write_text(
                "model Invoice {\n  id String @id\n  amount Float\n  user User @relation(fields: [userId], references: [id])\n}\n",
                encoding="utf-8",
            )
            rep = schema_mod.distill_workspace_schema(ws)
            self.assertEqual(rep["entity_count"], 3)
            self.assertIn("user_id->users", rep["compact_dsl"])
            self.assertGreater(rep["token_savings_pct"], 50.0)

    def test_34_shadow_preflight_syntax_brace_and_import_guard(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            ws = Path(tmp)
            (ws / "broken.py").write_text("def oops(\n    return 1\n", encoding="utf-8")
            (ws / "broken.ts").write_text("import { x } from './missing_mod';\nexport function f() {\n  if (true) {\n", encoding="utf-8")
            (ws / "clean.py").write_text("def ok() -> int:\n    return 42\n", encoding="utf-8")

            bad = shadow_mod.run_shadow_check(ws, ["broken.py", "broken.ts"])
            self.assertFalse(bad["passed"])
            kinds = {i["kind"] for i in bad["issues"]}
            self.assertIn("python_syntax_error", kinds)
            self.assertIn("unclosed_delimiter", kinds)
            self.assertIn("broken_relative_import", kinds)

            good = shadow_mod.run_shadow_check(ws, ["clean.py"])
            self.assertTrue(good["passed"])

    def test_35_session_time_machine_checkpoint_and_surgical_restore(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            ws = Path(tmp)
            f = ws / "service.py"
            f.write_text("VERSION = 1\n", encoding="utf-8")
            cp = tm_mod.create_checkpoint(ws, label="clean-v1")
            self.assertEqual(cp["file_count"], 1)

            f.write_text("VERSION = 999  # broken\n", encoding="utf-8")
            diff = tm_mod.diff_checkpoint(ws, cp["id"])
            self.assertIn("service.py", diff["modified"])

            tm_mod.restore_checkpoint(ws, cp["id"])
            self.assertEqual(f.read_text(encoding="utf-8"), "VERSION = 1\n")

    def test_36_github_ci_shield_and_cloud_share_card(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            ws = Path(tmp)
            ci = ci_mod.install_ci_shield(ws)
            self.assertTrue(ci["installed"])
            self.assertTrue((ws / ".github" / "workflows" / "sqo-shield.yml").is_file())

        card = share_mod.build_share_payload(REPO_ROOT / "skills", handle="ElNeMeR")
        self.assertEqual(card["handle"], "ElNeMeR")
        self.assertIn("https://sqo.elnemer-ai.com/api/card.php", card["live_card_url"])

    def test_37_anti_hallucination_dependency_verifier(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            ws = Path(tmp)
            (ws / "package.json").write_text(json.dumps({"dependencies": {"zod": "^3.22.0", "unused-pkg": "1.0.0"}}), encoding="utf-8")
            (ws / "index.ts").write_text("import { z } from 'zod';\nimport { magic } from 'hallucinated-ai-sdk';\n", encoding="utf-8")
            rep = vdeps_mod.verify_workspace_dependencies(ws)
            self.assertFalse(rep["clean"])
            self.assertEqual(rep["phantom_imports"][0]["package"], "hallucinated-ai-sdk")
            self.assertEqual(rep["unused_dependencies"][0]["package"], "unused-pkg")

    def test_38_universal_i18n_drift_and_placeholder_auditor(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            ws = Path(tmp)
            l10n = ws / "lib" / "l10n"
            l10n.mkdir(parents=True)
            (l10n / "app_en.arb").write_text(json.dumps({"hello": "Hello {userName}", "logout": "Sign out"}), encoding="utf-8")
            (l10n / "app_ar.arb").write_text(json.dumps({"hello": "مرحباً {wrongVar}"}), encoding="utf-8")
            rep = i18n_mod.audit_workspace_i18n(ws)
            self.assertEqual(rep["total_missing_keys"], 1)
            self.assertEqual(rep["total_placeholder_mismatches"], 1)

    def test_39_sha256_file_bound_semantic_memoization_cache(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            ws = Path(tmp)
            f = ws / "auth.py"
            f.write_text("TOKEN_TTL = 3600\n", encoding="utf-8")
            memo_mod.memo_put(ws, "What is auth TTL?", "Auth TTL is 3600s", ["auth.py"])
            hit = memo_mod.memo_get(ws, "what is   AUTH ttl?")
            self.assertEqual(hit["status"], "HIT")

            f.write_text("TOKEN_TTL = 7200\n", encoding="utf-8")
            stale = memo_mod.memo_get(ws, "What is auth TTL?")
            self.assertEqual(stale["status"], "STALE_INVALIDATED")

    def test_40_backend_to_frontend_openapi_contract_extractor(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            ws = Path(tmp)
            (ws / "server.py").write_text("@app.get('/api/orders/{order_id}')\ndef get_order(order_id: str):\n    return {}\n", encoding="utf-8")
            rep = contracts_mod.extract_api_contracts(ws)
            self.assertEqual(rep["endpoint_count"], 1)
            self.assertIn("/api/orders/{order_id}", rep["openapi_3_1"]["paths"])

    def test_41_autonomous_multi_model_swarm_planner(self) -> None:
        bp = swarm_plan_mod.build_swarm_blueprint(REPO_ROOT / "skills", "Audit auth jwt security and refactor helpers", max_workers=3)
        self.assertTrue(bp["collision_free_guarantee"])
        self.assertGreaterEqual(len(bp["workers"]), 1)
        self.assertGreater(bp["frontier_quota_savings_pct"], 50.0)

    def test_42_cloud_golden_rules_hub_offline_and_pull(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            ws = Path(tmp)
            (ws / "pubspec.yaml").write_text("name: demo\n", encoding="utf-8")
            pulled = hub_mod.pull_into_workspace(ws, stack="auto", online=False)
            self.assertEqual(pulled["stack"], "flutter")
            self.assertGreaterEqual(pulled["imported_rules"], 1)

    def test_43_surgical_symbol_editor_and_syntax_auto_rollback(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            ws = Path(tmp)
            py_f = ws / "billing.py"
            py_f.write_text(
                "# Header padding\n" * 40
                + "class BillingService:\n"
                + "    def calc_total(self, price: float) -> float:\n"
                + "        return price * 1.0\n\n"
                + "    def keep_me(self) -> str:\n"
                + "        return BillingService().calc_total(10.0)\n",
                encoding="utf-8",
            )
            callers = sym_mod.find_callers(ws, "calc_total")
            self.assertGreaterEqual(callers["total_hits"], 2)

            res = sym_mod.mutate_symbol(
                ws,
                py_f,
                "BillingService.calc_total",
                "replace",
                "def calc_total(self, price: float, tax: float = 0.14) -> float:\n    return round(price * (1.0 + tax), 2)",
            )
            self.assertTrue(res["ok"])
            self.assertGreater(res["output_token_savings_pct"], 50.0)
            self.assertIn("tax: float = 0.14", py_f.read_text(encoding="utf-8"))

            # Inject broken syntax -> must auto-rollback!
            bad = sym_mod.mutate_symbol(ws, py_f, "BillingService.calc_total", "replace", "def calc_total(self:\n    return 0")
            self.assertFalse(bad["ok"])
            self.assertTrue(bad.get("rolled_back"))
            self.assertIn("tax: float = 0.14", py_f.read_text(encoding="utf-8"))

    def test_44_spec_driven_dag_engine_and_acceptance_gate(self) -> None:
        import sys
        with tempfile.TemporaryDirectory() as tmp:
            ws = Path(tmp)
            sp = spec_mod.init_spec(
                ws,
                "Stripe Webhook Auth",
                "Verify webhook signatures safely",
                tasks=[
                    {"step_key": "T1", "title": "Write signature verifier", "owned_files": ["auth.py"], "depends_on": [], "verify_cmd": f'"{sys.executable}" -c "import sys; sys.exit(1)"'},
                    {"step_key": "T2", "title": "Wire endpoint", "owned_files": ["api.py"], "depends_on": ["T1"], "verify_cmd": f'"{sys.executable}" -c "import sys; sys.exit(0)"'},
                ],
            )
            self.assertTrue(sp["ok"])
            nxt = spec_mod.get_next_task(ws, sp["slug"])
            self.assertEqual(nxt["task"]["step_key"], "T1")

            blocked = spec_mod.complete_task(ws, sp["slug"], "T1", run_verify=True)
            self.assertFalse(blocked["ok"])
            self.assertTrue(blocked.get("gate_blocked"))

            done1 = spec_mod.complete_task(ws, sp["slug"], "T1", run_verify=False)
            self.assertTrue(done1["ok"])
            self.assertEqual(done1["next_task"]["step_key"], "T2")

    def test_45_auto_captured_temporal_memory_graph_and_hook(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            ws = Path(tmp)
            (ws / ".sqo").mkdir()
            f1 = ws / "auth.py"
            f2 = ws / "jwt.py"
            f1.write_text("x = 1\n", encoding="utf-8")
            f2.write_text("y = 2\n", encoding="utf-8")

            state_dir = ws / "state"
            hook_mod.evaluate_post_tool(
                {"conversationId": "c-graph", "toolCall": {"name": "run_command", "args": {"CommandLine": "pytest tests/test_auth.py"}}, "error": "exit 1"},
                state_root=state_dir,
            )
            hook_mod.evaluate_post_tool(
                {"conversationId": "c-graph", "toolCall": {"name": "edit_file", "args": {"Path": str(f1)}}},
                state_root=state_dir,
            )
            hook_mod.evaluate_post_tool(
                {"conversationId": "c-graph", "toolCall": {"name": "edit_file", "args": {"Path": str(f2)}}},
                state_root=state_dir,
            )
            hook_mod.evaluate_post_tool(
                {"conversationId": "c-graph", "toolCall": {"name": "run_command", "args": {"CommandLine": "pytest tests/test_auth.py"}}, "error": ""},
                state_root=state_dir,
            )

            hist = mgraph_mod.query_file_history(ws, "jwt.py")
            self.assertGreaterEqual(hist["touch_count"], 1)
            rels = {r["rel"] for r in hist["relations"]}
            self.assertIn("CO_EDITED_WITH", rels)
            self.assertIn("RESOLVED_FAILURE", rels)

    def test_46_karpathy_diff_laziness_deletion_and_scope_auditor(self) -> None:
        bad_diff = (
            "diff --git a/src/unrequested.py b/src/unrequested.py\n"
            "--- a/src/unrequested.py\n"
            "+++ b/src/unrequested.py\n"
            "@@ -1,4 +1,3 @@\n"
            "-def important_existing_feature():\n"
            "-    return True\n"
            "+def half_baked():\n"
            "+    # TODO: implement rest of logic\n"
        )
        rep = karp_mod.audit_diff_text(bad_diff, allowed_files=["src/auth.py"])
        self.assertFalse(rep["passed"])
        kinds = {f["kind"] for f in rep["findings"]}
        self.assertIn("laziness_placeholder", kinds)
        self.assertIn("silent_feature_deletion", kinds)
        self.assertIn("scope_creep", kinds)

        clean_diff = (
            "diff --git a/src/auth.py b/src/auth.py\n"
            "--- a/src/auth.py\n"
            "+++ b/src/auth.py\n"
            "@@ -1,2 +1,3 @@\n"
            " def verify_token(tok: str) -> bool:\n"
            "+    if not tok: return False\n"
            "     return len(tok) > 10\n"
        )
        ok_rep = karp_mod.audit_diff_text(clean_diff, allowed_files=["src/auth.py"])
        self.assertTrue(ok_rep["passed"])
        self.assertEqual(ok_rep["grade"], "A+")

    def test_47_live_sdk_version_and_deprecation_radar(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            ws = Path(tmp)
            (ws / "pubspec.yaml").write_text("name: app\ndependencies:\n  go_router: ^14.0.0\n", encoding="utf-8")
            (ws / "screen.dart").write_text(
                "Widget build(ctx) => WillPopScope(child: Container(color: Colors.blue.withOpacity(0.5)));\n",
                encoding="utf-8",
            )
            rep = sdk_mod.scan_sdk_deprecations(ws)
            self.assertFalse(rep["clean"])
            self.assertGreaterEqual(rep["deprecation_count"], 2)

    def test_48_isolated_worktree_sandbox_diff_and_promote(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            ws = Path(tmp)
            (ws / "core.py").write_text("VAL = 1\n", encoding="utf-8")
            sb = sandbox_mod.create_sandbox(ws, "exp-refactor")
            self.assertTrue(sb["ok"])
            sb_file = Path(sb["path"]) / "core.py"
            sb_file.write_text("VAL = 2\n", encoding="utf-8")
            # Main workspace untouched!
            self.assertEqual((ws / "core.py").read_text(encoding="utf-8"), "VAL = 1\n")

            d = sandbox_mod.diff_sandbox(ws, "exp-refactor")
            self.assertIn("core.py", d["modified"])

            sandbox_mod.promote_sandbox(ws, "exp-refactor")
            self.assertEqual((ws / "core.py").read_text(encoding="utf-8"), "VAL = 2\n")
            sandbox_mod.cleanup_sandbox(ws, "exp-refactor")


if __name__ == "__main__":
    unittest.main()
