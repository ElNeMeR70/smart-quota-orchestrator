#!/usr/bin/env python3
"""OWASP Top-10 & Agentic Security SAST Gatekeeper (`security_sast.py` — v11.0 Hypernova).

Ultra-fast (<15ms), zero-dependency Static Application Security Testing (SAST) scanner
built specifically for vulnerabilities frequently hallucinated by AI coding agents across
Python, TypeScript/JavaScript, PHP/Laravel, Dart/Flutter, and Go.
"""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from typing import Any, Dict, List

SAST_RULES = [
    {
        "id": "SAST-SQLI-01",
        "cwe": "CWE-89",
        "severity": "critical",
        "title": "SQL Injection via String Interpolation",
        "exts": {".py", ".ts", ".tsx", ".js", ".jsx", ".php", ".dart", ".go"},
        "pattern": re.compile(
            r"""(?:f["'][^"']*\b(?:SELECT|INSERT\s+INTO|UPDATE\s+\w+\s+SET|DELETE\s+FROM)\b[^"']*\{[^}]+\}|`[^`]*\b(?:SELECT|INSERT\s+INTO|UPDATE\s+\w+\s+SET|DELETE\s+FROM)\b[^`]*\$\{[^}]+\}|["']\s*(?:SELECT|DELETE\s+FROM|UPDATE)\b[^"']*["']\s*(?:\+|\.\s*\$))""",
            re.IGNORECASE,
        ),
        "remediation": "Use parameterized queries (`?` / `$1` / `:param`) or ORM bound parameters instead of f-strings/template literals.",
    },
    {
        "id": "SAST-CMDI-02",
        "cwe": "CWE-78",
        "severity": "critical",
        "title": "OS Command Injection Sink (`shell=True` / `os.system` / `exec`)",
        "exts": {".py", ".ts", ".js", ".php"},
        "pattern": re.compile(
            r"""(?:\bos\.system\s*\(\s*f["']|subprocess\.(?:run|Popen|call)\s*\(\s*f["'][^)]*shell\s*=\s*True|\bchild_process\.exec\s*\(\s*`[^`]*\$\{|\b(?:shell_exec|passthru|system)\s*\(\s*\$_(?:GET|POST|REQUEST))"""
        ),
        "remediation": "Pass argument arrays (`['cmd', arg]`) with `shell=False` and validate inputs strictly.",
    },
    {
        "id": "SAST-XSS-03",
        "cwe": "CWE-79",
        "severity": "high",
        "title": "Unescaped DOM / Template XSS Sink",
        "exts": {".tsx", ".jsx", ".ts", ".js", ".php", ".vue"},
        "pattern": re.compile(
            r"""(?:dangerouslySetInnerHTML\s*=\s*\{\s*\{\s*__html\s*:|v-html\s*=|\becho\s+\$_(?:GET|POST|REQUEST)\b|\.innerHTML\s*=\s*(?!["']\s*["']))"""
        ),
        "remediation": "Sanitize untrusted HTML with DOMPurify or render escaped text nodes (`textContent` / `htmlspecialchars`).",
    },
    {
        "id": "SAST-EVAL-04",
        "cwe": "CWE-95",
        "severity": "critical",
        "title": "Arbitrary Code Execution (`eval` / `pickle.loads` / `yaml.load`)",
        "exts": {".py", ".ts", ".js", ".php"},
        "pattern": re.compile(
            r"""(?:\beval\s*\(\s*(?![\s"']*['"])|\bpickle\.loads?\s*\(|\byaml\.load\s*\([^)]*(?!SafeLoader)\))"""
        ),
        "remediation": "Replace `eval()` with `json.loads` / `ast.literal_eval`, and use `yaml.safe_load()`.",
    },
    {
        "id": "SAST-CRYPTO-05",
        "cwe": "CWE-327",
        "severity": "medium",
        "title": "Weak Password Hashing or Insecure Token RNG",
        "exts": {".py", ".ts", ".js", ".php", ".dart"},
        "pattern": re.compile(
            r"""(?:hashlib\.(?:md5|sha1)\s*\([^)]*passw|md5\s*\(\s*\$\w*pass|Math\.random\s*\(\s*\)[^\n]*(?:token|secret|otp|key))""",
            re.IGNORECASE,
        ),
        "remediation": "Use Argon2id / bcrypt / scrypt for passwords and `secrets.token_urlsafe()` / `crypto.randomBytes()` for tokens.",
    },
    {
        "id": "SAST-CORS-06",
        "cwe": "CWE-942",
        "severity": "medium",
        "title": "Wildcard CORS with Credentials Enabled",
        "exts": {".py", ".ts", ".js", ".php"},
        "pattern": re.compile(
            r"""allow_origins\s*=\s*\[\s*["']\*["']\s*\][^\n]*allow_credentials\s*=\s*True"""
        ),
        "remediation": "Specify explicit trusted origins when `allow_credentials=True`.",
    },
]

SKIP_DIRS = {".git", "node_modules", ".venv", "venv", "__pycache__", "build", "dist", ".next", ".dart_tool", "vendor", ".sqo", "tests"}


def scan_code_snippet(code: str, virtual_ext: str = ".py") -> List[Dict[str, Any]]:
    hits: List[Dict[str, Any]] = []
    for ln_no, ln in enumerate(code.splitlines(), 1):
        stripped = ln.strip()
        if stripped.startswith(("#", "//", "*")):
            continue
        for rule in SAST_RULES:
            if virtual_ext in rule["exts"] and rule["pattern"].search(ln):
                hits.append(
                    {
                        "rule_id": rule["id"],
                        "cwe": rule["cwe"],
                        "severity": rule["severity"],
                        "title": rule["title"],
                        "line": ln_no,
                        "snippet": stripped[:110],
                        "remediation": rule["remediation"],
                    }
                )
    return hits


def scan_workspace_security(workspace: Path) -> Dict[str, Any]:
    workspace = workspace.resolve()
    findings: List[Dict[str, Any]] = []
    scanned_files = 0
    all_exts = set().union(*(r["exts"] for r in SAST_RULES))

    for p in workspace.rglob("*"):
        if not p.is_file() or p.suffix.lower() not in all_exts:
            continue
        if any(part in SKIP_DIRS for part in p.parts):
            continue
        if p.name == "security_sast.py":
            continue
        scanned_files += 1
        try:
            txt = p.read_text(encoding="utf-8", errors="ignore")
        except OSError:
            continue
        file_hits = scan_code_snippet(txt, p.suffix.lower())
        rel = str(p.relative_to(workspace)).replace("\\", "/")
        for h in file_hits:
            h["file"] = rel
            findings.append(h)
            if len(findings) >= 40:
                break
        if len(findings) >= 40:
            break

    crit = sum(1 for f in findings if f["severity"] == "critical")
    high = sum(1 for f in findings if f["severity"] == "high")
    score = max(0, 100 - crit * 30 - high * 18 - (len(findings) - crit - high) * 8)
    grade = "A+" if score >= 96 else ("A" if score >= 88 else ("B" if score >= 75 else ("C" if score >= 55 else "F")))

    return {
        "secure": crit == 0 and high == 0,
        "security_score": score,
        "grade": grade,
        "scanned_files": scanned_files,
        "finding_count": len(findings),
        "critical_count": crit,
        "findings": findings,
    }


def render_markdown(rep: Dict[str, Any]) -> str:
    icon = "🛡️ SECURE" if rep["secure"] else "🚨 VULNERABILITIES DETECTED"
    lines = [
        f"### {icon} — Agentic SAST Security Audit (`{rep['security_score']}/100` • Grade `{rep['grade']}`)",
        f"- **Scanned Source Files:** `{rep['scanned_files']}` | **Findings:** `{rep['finding_count']}` (`{rep['critical_count']}` critical)",
    ]
    for f in rep["findings"][:15]:
        lines.append(
            f"- **[{f['severity'].upper()} • {f['cwe']}]** `{f.get('file', 'snippet')}:L{f['line']}` — **{f['title']}**\n"
            f"  - Fix: {f['remediation']}"
        )
    if not rep["findings"]:
        lines.append("- ✅ **Zero OWASP SQLi, Command Injection, XSS, Eval, or Weak Crypto sinks detected!**")
    return "\n".join(lines)


def main() -> int:
    ap = argparse.ArgumentParser(description="OWASP & Agentic SAST Security Scanner")
    ap.add_argument("--workspace", default=".")
    ap.add_argument("--json", action="store_true")
    ns = ap.parse_args()
    rep = scan_workspace_security(Path(ns.workspace))
    print(json.dumps(rep, indent=2, ensure_ascii=False) if ns.json else render_markdown(rep))
    return 0 if rep["secure"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
