#!/usr/bin/env python3
"""Cloud & AI API Bill-Shock Preventer (`finops_guard.py` — v12.0 Quantum Edition).

World's first static FinOps & Wallet-Shock scanner for AI-generated SaaS codebases!
Detects runaway cloud billing traps before deployment ($500–$10,000+ overnight bills):
1. React `useEffect` with Firestore `onSnapshot` / `fetch` missing dependency array `[]` (Infinite Read/API Loop!)
2. Firebase Cloud Function (`onDocumentWritten` / `onUpdate`) writing back to the same collection without loop guard (Recursive $$$ Explosion!)
3. LLM API calls (`generate_content`, `chat.completions.create`, `messages.create`) inside `for`/`while` loops or missing `max_tokens`/`max_output_tokens` cap
4. Public Next.js / Express / FastAPI AI endpoints with zero rate-limiting middleware
"""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from typing import Any, Dict, List

LLM_CALL_RE = re.compile(
    r"(?:chat\.completions\.create|responses\.create|messages\.create|models\.generate_content|generateText|streamText)\s*\("
)
MAX_TOK_RE = re.compile(r"\b(?:max_tokens|max_output_tokens|maxTokens|maxOutputTokens)\b")
LOOP_HEADER_RE = re.compile(r"^\s*(?:for\s*\(|for\s+\w+\s+in\b|async\s+for\b|while\s*\()")
USE_EFFECT_INF_RE = re.compile(
    r"useEffect\s*\(\s*\(\s*\)\s*=>\s*\{[\s\S]{1,380}?(?:onSnapshot|getDocs|fetch|axios|supabase)\b[\s\S]{1,220}?\}\s*\)",
)
FIRESTORE_TRIGGER_SELF_WRITE_RE = re.compile(
    r"onDocument(?:Written|Updated|Created)\s*\(\s*['\"]([^/'\"]+)[^'\"]*['\"][\s\S]{1,650}?\.collection\s*\(\s*['\"]\1['\"]\s*\)\s*\.\s*(?:add|doc|set|update)\b"
)

SKIP_DIRS = {".git", "node_modules", ".venv", "venv", "__pycache__", "build", "dist", ".next", ".dart_tool", "vendor", ".sqo", "tests"}


def scan_finops_content(text: str, rel_file: str = "snippet") -> List[Dict[str, Any]]:
    risks: List[Dict[str, Any]] = []
    lines = text.splitlines()

    # 1. React useEffect missing dependency array with DB/API read -> Infinite $$$ loop
    for m in USE_EFFECT_INF_RE.finditer(text):
        snippet = m.group(0)
        # Check if there is a dependency array before the closing `);`
        if not re.search(r",\s*\[[^\]]*\]\s*\)\s*$", snippet.strip()):
            ln_no = text[: m.start()].count("\n") + 1
            risks.append(
                {
                    "id": "FINOPS-INF-USEEFFECT",
                    "severity": "critical",
                    "estimated_burn_risk": "$200–$2,500 / day",
                    "file": rel_file,
                    "line": ln_no,
                    "detail": "`useEffect` triggers Firestore/API reads without a `[]` dependency array — causes infinite render-read billing loop!",
                }
            )

    # 2. Recursive Cloud Function self-trigger
    for m in FIRESTORE_TRIGGER_SELF_WRITE_RE.finditer(text):
        col = m.group(1)
        ln_no = text[: m.start()].count("\n") + 1
        risks.append(
            {
                "id": "FINOPS-RECURSIVE-TRIGGER",
                "severity": "critical",
                "estimated_burn_risk": "$500–$10,000 / hr",
                "file": rel_file,
                "line": ln_no,
                "detail": f"Cloud Function triggered on `{col}` writes back to `{col}`! Add an idempotency guard field to prevent infinite billing recursion.",
            }
        )

    # 3. LLM calls inside loops or without max_tokens cap
    for idx, ln in enumerate(lines):
        if LOOP_HEADER_RE.search(ln):
            window = "\n".join(lines[idx + 1 : min(len(lines), idx + 12)])
            if LLM_CALL_RE.search(window):
                risks.append(
                    {
                        "id": "FINOPS-LLM-IN-LOOP",
                        "severity": "high",
                        "estimated_burn_risk": "$50–$800 / batch",
                        "file": rel_file,
                        "line": idx + 1,
                        "detail": "Paid LLM generation call inside loop! Batch items into a single structured-output prompt or add semantic caching.",
                    }
                )
        if LLM_CALL_RE.search(ln):
            call_window = "\n".join(lines[idx : min(len(lines), idx + 8)])
            if not MAX_TOK_RE.search(call_window):
                risks.append(
                    {
                        "id": "FINOPS-UNCAPPED-LLM",
                        "severity": "medium",
                        "estimated_burn_risk": "5x output token spike",
                        "file": rel_file,
                        "line": idx + 1,
                        "detail": "LLM API call has no explicit `max_tokens` / `max_output_tokens` ceiling against runaway generation.",
                    }
                )

    # 4. Unprotected AI HTTP Route without rate-limit check
    if ("app/api/" in rel_file or "routes/" in rel_file or "@app.post" in text) and LLM_CALL_RE.search(text):
        if not re.search(r"\b(?:ratelimit|rateLimit|RateLimiter|throttle|limiter|auth|getServerSession|verifyIdToken)\b", text, re.IGNORECASE):
            risks.append(
                {
                    "id": "FINOPS-UNRATED-AI-ENDPOINT",
                    "severity": "high",
                    "estimated_burn_risk": "Wallet-drain bot attack",
                    "file": rel_file,
                    "line": 1,
                    "detail": "HTTP endpoint invokes a paid LLM API with no visible auth or rate-limiter guard!",
                }
            )

    return risks


def audit_workspace_finops(workspace: Path) -> Dict[str, Any]:
    workspace = workspace.resolve()
    exts = {".py", ".ts", ".tsx", ".js", ".jsx", ".dart", ".php"}
    findings: List[Dict[str, Any]] = []
    scanned = 0

    for p in workspace.rglob("*"):
        if not p.is_file() or p.suffix.lower() not in exts:
            continue
        if any(part in SKIP_DIRS for part in p.parts) or p.name == "finops_guard.py":
            continue
        scanned += 1
        try:
            txt = p.read_text(encoding="utf-8", errors="ignore")
        except OSError:
            continue
        rel = str(p.relative_to(workspace)).replace("\\", "/")
        findings.extend(scan_finops_content(txt, rel))
        if len(findings) >= 35:
            break

    crit = sum(1 for f in findings if f["severity"] == "critical")
    high = sum(1 for f in findings if f["severity"] == "high")
    score = max(0, 100 - crit * 35 - high * 20 - (len(findings) - crit - high) * 8)

    return {
        "wallet_safe": crit == 0 and high == 0,
        "finops_score": score,
        "scanned_files": scanned,
        "risk_count": len(findings),
        "critical_count": crit,
        "risks": findings[:35],
    }


def render_markdown(rep: Dict[str, Any]) -> str:
    badge = "💰 WALLET SAFE" if rep["wallet_safe"] else "💸 CLOUD BILL-SHOCK RISK"
    lines = [
        f"### {badge} — Cloud & AI FinOps Guard (`{rep['finops_score']}/100`)",
        f"- **Scanned Files:** `{rep['scanned_files']}` | **Billing Traps Found:** `{rep['risk_count']}` (`{rep['critical_count']}` critical)",
    ]
    for r in rep["risks"][:15]:
        lines.append(
            f"- **[{r['severity'].upper()} • `{r['id']}` • Risk: {r['estimated_burn_risk']}]** `{r['file']}:L{r['line']}`\n"
            f"  - {r['detail']}"
        )
    if not rep["risks"]:
        lines.append("- ✅ **Zero infinite Firestore listeners, recursive triggers, or uncapped LLM wallet-drain loops!**")
    return "\n".join(lines)


def main() -> int:
    ap = argparse.ArgumentParser(description="Cloud & AI API Bill-Shock Preventer")
    ap.add_argument("--workspace", default=".")
    ap.add_argument("--json", action="store_true")
    ns = ap.parse_args()
    rep = audit_workspace_finops(Path(ns.workspace))
    print(json.dumps(rep, indent=2, ensure_ascii=False) if ns.json else render_markdown(rep))
    return 0 if rep["wallet_safe"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
