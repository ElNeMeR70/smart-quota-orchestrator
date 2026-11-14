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

    def test_18_mcp_stdio_server_20_tools(self) -> None:
        init_resp = mcp_mod.handle_rpc_message({"jsonrpc": "2.0", "id": 1, "method": "initialize", "params": {"protocolVersion": "2025-03-26"}})
        assert init_resp is not None
        self.assertEqual(init_resp["result"]["serverInfo"]["version"], "7.0.0")

        tools_resp = mcp_mod.handle_rpc_message({"jsonrpc": "2.0", "id": 2, "method": "tools/list"})
        assert tools_resp is not None
        tool_names = {t["name"] for t in tools_resp["result"]["tools"]}
        self.assertEqual(len(tool_names), 20)
        for expected in (
            "sqo_compress_prompt",
            "sqo_repo_badge",
            "sqo_init_preset",
            "sqo_context_health",
            "sqo_roi_ledger",
            "sqo_media_budget",
            "sqo_pinpoint_error",
            "sqo_code_hotspots",
            "sqo_api_routes",
            "sqo_cache_audit",
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
                self.assertEqual(data["version"], "7.0.0")
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

    def test_29_manifests_v7_complete(self) -> None:
        for mf in ("plugin.json", ".claude-plugin/plugin.json", "gemini-extension.json", "glama.json", "package.json", "vscode-extension/package.json"):
            data = json.loads((REPO_ROOT / mf).read_text(encoding="utf-8"))
            self.assertEqual(data["version"], "7.0.0")
        self.assertTrue((REPO_ROOT / "pyproject.toml").is_file())
        self.assertTrue((REPO_ROOT / "bin" / "sqo.js").is_file())
        self.assertTrue((REPO_ROOT / "vscode-extension" / "extension.js").is_file())
        tax = tax_mod.profile_workspace(REPO_ROOT / "skills")
        self.assertEqual(len(tax["skills"]), 6)

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


if __name__ == "__main__":
    unittest.main()
