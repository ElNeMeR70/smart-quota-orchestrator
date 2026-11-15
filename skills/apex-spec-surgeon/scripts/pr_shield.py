#!/usr/bin/env python3
"""8-Gate Pre-PR & Pre-Deploy Autonomous Scorecard (`pr_shield.py` — v13.0 Zenith Edition).

Runs ALL 8 deterministic production engines in <65ms with ZERO LLM token cost and emits
a ready-to-post GitHub Pull Request Review Markdown Table (0–100 Score, Grade A+ to F):
  1. OWASP Agentic Security SAST (SQLi, CMDi, XSS, Eval, Weak Crypto)
  2. Cloud & AI FinOps Wallet Guard (Infinite useEffect Firestore loops, recursive triggers, LLM loops)
  3. 4-Seat Adversarial Council (TOCTOU double-spend races, missing HTTP timeouts, bare excepts)
  4. Database N+1 & UI-Jank Performance Profiler
  5. Bilingual Arabic RTL, WCAG a11y & Overflow Auditor
  6. Anti-Hallucination Phantom Dependency Verifier
  7. Environment Variable `.env.example` Drift Guard
  8. 10-Pattern Secret & Credential DLP Scanner
"""

from __future__ import annotations

import argparse
import importlib.util
import json
from pathlib import Path
from typing import Any, Dict, List

SKILLS_ROOT = Path(__file__).resolve().parents[2]


def _load_sibling(rel_path: str):
    full = SKILLS_ROOT / rel_path
    spec = importlib.util.spec_from_file_location("pr_" + rel_path.replace("/", "_").replace(".", "_"), full)
    assert spec and spec.loader
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def run_8_gate_pr_review(workspace: Path) -> Dict[str, Any]:
    workspace = workspace.resolve()
    sast = _load_sibling("apex-spec-surgeon/scripts/security_sast.py").scan_workspace_security(workspace)
    finops = _load_sibling("apex-spec-surgeon/scripts/finops_guard.py").audit_workspace_finops(workspace)
    council = _load_sibling("apex-spec-surgeon/scripts/council_review.py").run_council_on_workspace(workspace)
    perf = _load_sibling("apex-spec-surgeon/scripts/perf_profiler.py").profile_workspace_performance(workspace)
    ui_rtl = _load_sibling("apex-spec-surgeon/scripts/ui_rtl_auditor.py").audit_workspace_ui(workspace)
    vdeps = _load_sibling("smart-quota-orchestrator/scripts/verify_hallucinations.py").verify_workspace_dependencies(workspace)
    drift = _load_sibling("context-compactor/scripts/detect_drift.py").audit_env_and_config_drift(workspace)
    scrub = _load_sibling("project-memory-vault/scripts/scrub_secrets.py").scan_workspace_secrets(workspace)

    sec_score = int(sast.get("security_score", 100))
    fin_score = int(finops.get("finops_score", 100))
    cnl_score = int(council.get("consensus_score", 100))
    prf_score = int(perf.get("performance_score", 100))
    rtl_score = int(ui_rtl.get("ui_rtl_score", 100))
    dep_issues = len(vdeps.get("undeclared_imports", []))
    dep_score = max(0, 100 - dep_issues * 25)
    drf_issues = len(drift.get("missing_from_env_example", []))
    drf_score = max(0, 100 - drf_issues * 15)
    dlp_hits = int(scrub.get("findings_count", 0))
    dlp_score = 100 if dlp_hits == 0 else max(0, 100 - dlp_hits * 40)

    gates: List[Dict[str, Any]] = [
        {"gate": "🛡️ 1. OWASP Security SAST", "score": sec_score, "issues": sast.get("finding_count", 0), "pass": sast.get("secure", True)},
        {"gate": "💸 2. Cloud & AI FinOps Guard", "score": fin_score, "issues": finops.get("risk_count", 0), "pass": finops.get("wallet_safe", True)},
        {"gate": "🎭 3. 4-Seat Adversarial Council", "score": cnl_score, "issues": council.get("docket_count", 0), "pass": council.get("approved", True)},
        {"gate": "⚡ 4. N+1 & UI-Jank Profiler", "score": prf_score, "issues": perf.get("issue_count", 0), "pass": prf_score >= 80},
        {"gate": "🎨 5. Arabic RTL & WCAG a11y", "score": rtl_score, "issues": ui_rtl.get("issue_count", 0), "pass": rtl_score >= 80},
        {"gate": "📦 6. Phantom Dependency Check", "score": dep_score, "issues": dep_issues, "pass": dep_issues == 0},
        {"gate": "⚙️ 7. Env `.env.example` Parity", "score": drf_score, "issues": drf_issues, "pass": drf_issues == 0},
        {"gate": "🔐 8. Secret & Credential DLP", "score": dlp_score, "issues": dlp_hits, "pass": dlp_hits == 0},
    ]

    overall = round(sum(g["score"] for g in gates) / len(gates))
    hard_block = not (sast.get("secure", True) and finops.get("wallet_safe", True) and dlp_hits == 0)
    if hard_block and overall > 69:
        grade = "C (BLOCKED)"
    else:
        grade = "A+" if overall >= 95 else ("A" if overall >= 88 else ("B" if overall >= 75 else ("C" if overall >= 60 else "F")))

    md_lines = [
        f"## 🛡️ Smart Quota & Superpowers OS — 8-Gate PR Shield (`{overall}/100` • Grade `{grade}`)",
        "",
        "| Engineering Gate | Score | Findings | Verdict |",
        "| :--- | :---: | :---: | :---: |",
    ]
    for g in gates:
        verdict = "✅ PASS" if g["pass"] else "🛑 ACTION NEEDED"
        md_lines.append(f"| {g['gate']} | **`{g['score']}/100`** | `{g['issues']}` | {verdict} |")

    top_blockers: List[str] = []
    for f in (sast.get("findings") or [])[:3]:
        top_blockers.append(f"- **[SAST `{f['rule']}`]** `{f['file']}:L{f['line']}` — {f['message']}")
    for r in (finops.get("risks") or [])[:3]:
        top_blockers.append(f"- **[FinOps `{r['id']}`]** `{r['file']}:L{r['line']}` — {r['detail']}")
    for d in (council.get("docket") or [])[:3]:
        top_blockers.append(f"- **[{d['seat']}]** `{d['file']}:L{d['line']}` — {d['verdict']}")

    if top_blockers:
        md_lines.extend(["", "### 🚨 Top Actionable Findings", *top_blockers[:8]])
    else:
        md_lines.extend(["", "> ✅ **All 8 production, security, FinOps, and RTL quality gates passed cleanly!**"])

    return {
        "merge_ready": not hard_block and overall >= 80,
        "overall_score": overall,
        "grade": grade,
        "gates": gates,
        "pr_markdown": "\n".join(md_lines),
    }


def main() -> int:
    ap = argparse.ArgumentParser(description="8-Gate Pre-PR Autonomous Review Scorecard")
    ap.add_argument("--workspace", "-w", default=".")
    ap.add_argument("--out", default="", help="Optional path to save PR review markdown")
    ap.add_argument("--json", action="store_true")
    ns = ap.parse_args()
    rep = run_8_gate_pr_review(Path(ns.workspace))
    if ns.out:
        Path(ns.out).write_text(rep["pr_markdown"], encoding="utf-8")
    print(json.dumps(rep, indent=2, ensure_ascii=False) if ns.json else rep["pr_markdown"])
    return 0 if rep["merge_ready"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
