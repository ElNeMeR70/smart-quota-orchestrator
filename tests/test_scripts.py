#!/usr/bin/env python3
"""Unit and integration tests for Smart Quota & Swarm Orchestrator CLI tools."""

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


parse_quota = _load_module(
    "parse_quota_pools",
    "skills/smart-quota-orchestrator/scripts/parse_quota_pools.py",
)
complexity = _load_module(
    "analyze_task_complexity",
    "skills/smart-quota-orchestrator/scripts/analyze_task_complexity.py",
)
audit_burn = _load_module(
    "audit_session_burn",
    "skills/smart-quota-orchestrator/scripts/audit_session_burn.py",
)
handoff = _load_module(
    "build_handoff_brief",
    "skills/context-compactor/scripts/build_handoff_brief.py",
)


class SmartQuotaOrchestratorTests(unittest.TestCase):
    def test_parse_quota_pools_groups_shared_and_reserve_pools(self) -> None:
        sample_payload = {
            "models": [
                "gemini-4-carbon-medium",
                "gemini-4-argon-medium",
                "gemini-4-hydrogen-medium",
                "gemini-pro-orchestrator",
                "claude-sonnet-4-6",
                "gpt-oss-120b-medium",
            ],
            "display_names": {
                "gemini-4-carbon-medium": "Gemini 4 Carbon (Medium)",
                "gemini-4-argon-medium": "Gemini 4 Argon (Medium)",
                "gemini-4-hydrogen-medium": "Gemini 4 Hydrogen (Medium)",
                "gemini-pro-orchestrator": "Orchestrator (Carbon)",
                "claude-sonnet-4-6": "Claude Sonnet 4.6 (Thinking)",
                "gpt-oss-120b-medium": "GPT-OSS 120B (Medium)",
            },
            "quotas": {
                "gemini-4-carbon-medium": {"quota_remaining": "36%", "quota_resets": "2026-11-14T06:00:00Z"},
                "gemini-4-argon-medium": {"quota_remaining": "36%", "quota_resets": "2026-11-14T06:00:00Z"},
                "gemini-4-hydrogen-medium": {"quota_remaining": "36%", "quota_resets": "2026-11-14T06:00:00Z"},
                "gemini-pro-orchestrator": {"quota_remaining": "36%", "quota_resets": "2026-11-14T06:00:00Z"},
                "claude-sonnet-4-6": {"quota_remaining": "100%", "quota_resets": "2026-11-14T09:00:00Z"},
                "gpt-oss-120b-medium": {"quota_remaining": "100%", "quota_resets": "2026-11-14T09:00:00Z"},
            },
        }
        now = dt.datetime(2026, 11, 14, 4, 0, 0, tzinfo=dt.timezone.utc)
        report = parse_quota.analyze_pools(sample_payload, now_utc=now)
        self.assertEqual(report["pool_count"], 3)
        gemini_pool = report["pools"][0]
        self.assertEqual(gemini_pool["pool_name"], "Google Gemini Pool")
        self.assertEqual(gemini_pool["health"], "CONSERVE")
        self.assertEqual(gemini_pool["safe_burn_pct_per_hour"], 18.0)
        md = parse_quota.render_markdown(report)
        self.assertIn("Live Quota Pool Dashboard", md)

    def test_analyze_task_complexity_detects_risk_and_parallelism(self) -> None:
        res = complexity.evaluate_task(
            REPO_ROOT,
            "Audit all files for auth jwt secret leaks and refactor stripe webhook billing",
            [],
        )
        self.assertGreaterEqual(res["complexity_score"], 35)
        self.assertIn("security_auth", res["risk_domains"])
        self.assertIn("payments_billing", res["risk_domains"])
        self.assertTrue(res["batch_fanout_detected"])

    def test_audit_session_burn_flags_redundant_reads_and_error_streaks(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            t_path = Path(tmp) / "transcript.jsonl"
            steps = [
                {"step_index": 1, "status": "DONE", "tool_calls": [{"name": "read_file", "arguments": {"Path": "/repo/a.py"}}]},
                {"step_index": 2, "status": "DONE", "tool_calls": [{"name": "read_file", "arguments": {"Path": "/repo/a.py"}}]},
                {"step_index": 3, "status": "ERROR", "content": "fail 1"},
                {"step_index": 4, "status": "ERROR", "content": "fail 2"},
                {"step_index": 5, "status": "ERROR", "content": "fail 3"},
            ]
            t_path.write_text("\n".join(json.dumps(s) for s in steps), encoding="utf-8")
            report = audit_burn.audit_transcript(t_path)
            self.assertEqual(report["redundant_file_reads"].get("/repo/a.py"), 1)
            self.assertEqual(report["max_consecutive_errors"], 3)

    def test_build_handoff_brief_outputs_compact_markdown(self) -> None:
        brief = handoff.build_brief(REPO_ROOT, "Ship v1.0.0", ["Run unit tests", "Push to GitHub"])
        md = handoff.render_markdown(brief)
        self.assertIn("Ship v1.0.0", md)
        self.assertLess(len(md), 2000)

    def test_manifests_and_skill_frontmatter_valid(self) -> None:
        plugin_data = json.loads((REPO_ROOT / "plugin.json").read_text(encoding="utf-8"))
        self.assertEqual(plugin_data["name"], "smart-quota-orchestrator")
        for skill_dir in ("smart-quota-orchestrator", "context-compactor"):
            skill_md = (REPO_ROOT / "skills" / skill_dir / "SKILL.md").read_text(encoding="utf-8")
            self.assertTrue(skill_md.startswith("---\nname: "))


if __name__ == "__main__":
    unittest.main()
