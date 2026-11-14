#!/usr/bin/env python3
"""Comprehensive test suite for Smart Quota & Swarm Orchestrator v2.0 (all 12 CLI tools + manifests)."""

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

handoff = _load_module("build_handoff_brief", "skills/context-compactor/scripts/build_handoff_brief.py")
outline_mod = _load_module("smart_outline", "skills/context-compactor/scripts/smart_outline.py")
diff_mod = _load_module("compress_git_diff", "skills/context-compactor/scripts/compress_git_diff.py")
denoise_mod = _load_module("compact_command_output", "skills/context-compactor/scripts/compact_command_output.py")
ignore_mod = _load_module("generate_agent_ignore", "skills/context-compactor/scripts/generate_agent_ignore.py")

slice_mod = _load_module("partition_parallel_slices", "skills/parallel-slice-architect/scripts/partition_parallel_slices.py")
tax_mod = _load_module("optimize_prompt_rules", "skills/prompt-tax-profiler/scripts/optimize_prompt_rules.py")


class SmartQuotaSuiteV2Tests(unittest.TestCase):
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
        res = complexity.evaluate_task(REPO_ROOT, "Audit all files for auth jwt secret leaks and stripe billing", [])
        self.assertIn("security_auth", res["risk_domains"])
        self.assertIn("payments_billing", res["risk_domains"])
        self.assertTrue(res["batch_fanout_detected"])

    def test_03_simulate_workflow_cost(self) -> None:
        sim = simulate_mod.simulate(files=15, avg_loc=250, turns=18)
        self.assertEqual(len(sim["strategies"]), 5)
        best_savings = max(s["quota_savings_vs_carbon_high_pct"] for s in sim["strategies"])
        self.assertGreater(best_savings, 50.0)

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
        self.assertGreaterEqual(outline["symbol_count"], 5)
        sym = outline_mod.extract_symbol_source(target, outline, "analyze_pools")
        self.assertIsNotNone(sym)
        assert sym is not None
        self.assertIn("def analyze_pools", sym["code"])

    def test_06_compress_git_diff_strips_lockfiles(self) -> None:
        sample_diff = (
            "diff --git a/package-lock.json b/package-lock.json\n"
            "--- a/package-lock.json\n+++ b/package-lock.json\n@@ -1 +1 @@\n-old\n+new\n"
            "diff --git a/src/auth.ts b/src/auth.ts\n"
            "--- a/src/auth.ts\n+++ b/src/auth.ts\n@@ -1 +1,2 @@\n export function verifyJwt() {}\n+// check signature\n"
        )
        res = diff_mod.compress_diff(sample_diff, max_tokens=500)
        self.assertEqual(len(res["skipped_lock_or_generated"]), 1)
        self.assertEqual(res["included_diffs"][0]["file"], "src/auth.ts")

    def test_07_compact_command_output_denoises_ansi_and_passing_spam(self) -> None:
        noisy = "\n".join(
            [f"\x1b[32mPASS\x1b[0m tests/unit/test_{i}.spec.ts" for i in range(40)]
            + [
                "FAIL tests/auth/login.spec.ts",
                "  AssertionError: expected 401 to equal 200 at src/auth.ts:42:13",
                "    at Object.<anonymous> (node_modules/jest-runner/build/index.js:10:5)",
                "Tests: 1 failed, 40 passed, 41 total",
            ]
        )
        res = denoise_mod.denoise_output(noisy, exit_code=1)
        self.assertGreater(res["token_savings_pct"], 50)
        self.assertTrue(any("AssertionError" in ln for ln in res["diagnostic_lines"]))
        self.assertFalse(any("node_modules" in ln for ln in res["diagnostic_lines"]))

    def test_08_partition_parallel_slices_and_emit_workflow(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            ws = Path(tmp)
            (ws / "types").mkdir()
            (ws / "auth").mkdir()
            (ws / "billing").mkdir()
            (ws / "types" / "shared.ts").write_text("export interface User { id: string; }\n", encoding="utf-8")
            (ws / "auth" / "login.ts").write_text("import { User } from '../types/shared';\nexport const login = () => {};\n", encoding="utf-8")
            (ws / "billing" / "charge.ts").write_text("import { User } from '../types/shared';\nexport const charge = () => {};\n", encoding="utf-8")

            plan = slice_mod.partition_workspace(ws, [], max_workers=3)
            stage0_files = [x["file"] for x in plan["stage_0_shared_contracts"]]
            self.assertIn("types/shared.ts", stage0_files)
            self.assertEqual(len(plan["stage_1_parallel_slices"]), 2)
            wf = slice_mod.emit_workflow_script(plan, "Add audit logging")
            self.assertIn("await parallel(", wf)

    def test_09_prompt_tax_profiler_and_ignore_guard(self) -> None:
        tax = tax_mod.profile_workspace(REPO_ROOT)
        self.assertEqual(len(tax["skills"]), 4)
        self.assertTrue(all(s["has_valid_frontmatter"] for s in tax["skills"]))
        bombs = ignore_mod.scan_token_bombs(REPO_ROOT)
        self.assertIn("node_modules/", bombs["generated_ignore_content"])

    def test_10_html_dashboard_and_master_sqo_cli(self) -> None:
        html_doc = dashboard_mod.build_dashboard_html(REPO_ROOT, REPO_ROOT / "skills")
        self.assertIn("Smart Quota &amp; Swarm Orchestrator", html_doc)
        proc = subprocess.run(
            [sys.executable, str(REPO_ROOT / "sqo.py"), "handoff", "--workspace", str(REPO_ROOT), "--goal", "Release v2.0"],
            capture_output=True,
            text=True,
            encoding="utf-8",
            check=False,
        )
        self.assertEqual(proc.returncode, 0)
        self.assertIn("Compact Handoff Brief", proc.stdout)

    def test_11_manifests_v2_valid(self) -> None:
        plugin_data = json.loads((REPO_ROOT / "plugin.json").read_text(encoding="utf-8"))
        self.assertEqual(plugin_data["version"], "2.0.0")
        for agent_md in ("quota-planner.md", "token-auditor.md"):
            self.assertTrue((REPO_ROOT / "agents" / agent_md).is_file())


if __name__ == "__main__":
    unittest.main()
