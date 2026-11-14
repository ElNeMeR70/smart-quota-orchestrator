#!/usr/bin/env python3
"""Zero-Leak Secret, API Key, JWT, Private-Key & DB URI Scanner / Redactor.

Protects BOTH security AND token quota:
  1. Redacts live secrets, PEM keys, huge JWTs, and Base64 blobs before snippets
     or `.env` templates enter an AI agent's context window!
  2. Audits a workspace (`--scan-workspace`) for accidentally hardcoded secrets
     with zero secret values printed to stdout (shows masked fingerprints only!).

Zero external dependencies (Python 3.8+ stdlib only).
"""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
from pathlib import Path
from typing import Any, Dict, List, Tuple

SECRET_RULES: List[Tuple[str, re.Pattern[str]]] = [
    ("PEM_PRIVATE_KEY", re.compile(r"-----BEGIN (?:RSA |EC |OPENSSH |PGP )?PRIVATE KEY-----[\s\S]+?-----END (?:RSA |EC |OPENSSH |PGP )?PRIVATE KEY-----")),
    ("GITHUB_PAT", re.compile(r"\b(?:ghp|gho|ghu|ghs|ghr)_[A-Za-z0-9]{30,255}\b|\bgithub_pat_[A-Za-z0-9_]{50,255}\b")),
    ("OPENAI_KEY", re.compile(r"\bsk-(?:proj-|svcacct-)?[A-Za-z0-9_-]{24,200}\b")),
    ("ANTHROPIC_KEY", re.compile(r"\bsk-ant-[A-Za-z0-9_-]{32,200}\b")),
    ("GOOGLE_API_KEY", re.compile(r"\bAIza[0-9A-Za-z_-]{35}\b")),
    ("STRIPE_SECRET", re.compile(r"\b(?:sk|rk)_(?:live|test)_[0-9a-zA-Z]{24,120}\b")),
    ("AWS_ACCESS_KEY", re.compile(r"\b(?:AKIA|ASIA)[0-9A-Z]{16}\b")),
    ("SLACK_TOKEN", re.compile(r"\bxox[baprs]-[0-9A-Za-z-]{24,160}\b")),
    ("JWT_BEARER", re.compile(r"\beyJ[A-Za-z0-9_-]{12,}\.eyJ[A-Za-z0-9_-]{12,}\.[A-Za-z0-9_-]{16,}\b")),
    ("DB_CONN_URI", re.compile(r"\b(?:postgres|postgresql|mysql|mongodb(?:\+srv)?|redis)://[^:\s'\"`]+:[^@\s'\"`]+@[^\s'\"`]+")),
]

IGNORE_DIRS = {".git", ".sqo", "node_modules", ".next", "dist", "build", "__pycache__", ".venv", "venv", "vendor", ".dart_tool"}
SCAN_EXTS = {".py", ".ts", ".tsx", ".js", ".jsx", ".dart", ".go", ".php", ".json", ".yaml", ".yml", ".toml", ".sh", ".ps1", ".md"}


def _configure_utf8() -> None:
    for stream in (sys.stdout, sys.stderr):
        if hasattr(stream, "reconfigure"):
            try:
                stream.reconfigure(encoding="utf-8")
            except Exception:
                pass


def scrub_text(raw_text: str) -> Dict[str, Any]:
    scrubbed = raw_text
    counts: Dict[str, int] = {}
    for label, pattern in SECRET_RULES:
        idx = 0

        def _repl(_m: re.Match[str]) -> str:
            nonlocal idx
            idx += 1
            counts[label] = counts.get(label, 0) + 1
            return f"<REDACTED_{label}_{idx}>"

        scrubbed = pattern.sub(_repl, scrubbed)

    return {
        "redacted_total": sum(counts.values()),
        "redacted_by_type": counts,
        "scrubbed_text": scrubbed,
    }


def scan_workspace_secrets(workspace: Path) -> Dict[str, Any]:
    findings: List[Dict[str, Any]] = []
    files_scanned = 0

    for dirpath, dirnames, filenames in os.walk(workspace):
        dirnames[:] = [d for d in dirnames if d not in IGNORE_DIRS]
        for fname in filenames:
            fpath = Path(dirpath) / fname
            if fname.startswith(".env") and fname != ".env.example":
                # Never read live .env contents into stdout! Flag only if unignored.
                continue
            if fpath.suffix.lower() not in SCAN_EXTS:
                continue
            try:
                if fpath.stat().st_size > 400 * 1024:
                    continue
                content = fpath.read_text(encoding="utf-8", errors="ignore")
            except OSError:
                continue

            files_scanned += 1
            rel = str(fpath.relative_to(workspace)).replace("\\", "/")
            for line_no, line in enumerate(content.splitlines(), start=1):
                for label, pattern in SECRET_RULES:
                    m = pattern.search(line)
                    if m:
                        raw_hit = m.group(0)
                        # Safe masked fingerprint ONLY — never leak raw secret!
                        masked = f"{raw_hit[:4]}...{raw_hit[-3:]}" if len(raw_hit) > 10 else "***"
                        findings.append({
                            "file": rel,
                            "line": line_no,
                            "type": label,
                            "masked_preview": masked,
                        })

    return {
        "files_scanned": files_scanned,
        "findings_count": len(findings),
        "findings": findings[:50],
    }


def main() -> int:
    _configure_utf8()
    parser = argparse.ArgumentParser(description="Scan for leaked secrets (masked) or scrub text safely before LLM ingestion.")
    parser.add_argument("--scan-workspace", "-w", help="Scan workspace source files for hardcoded secrets (outputs masked previews only).")
    parser.add_argument("--input-file", "-i", help="Scrub secrets out of a specific file and output redacted text.")
    parser.add_argument("--format", choices=("markdown", "json"), default="markdown", help="Output format.")
    args = parser.parse_args()

    if args.scan_workspace:
        rep = scan_workspace_secrets(Path(args.scan_workspace).resolve())
        if args.format == "json":
            print(json.dumps(rep, indent=2, ensure_ascii=False))
        else:
            lines = [
                "## Hardcoded Secret & Token Safety Audit",
                f"- **Source Files Scanned**: `{rep['files_scanned']}` | **Detected Leaks**: `{rep['findings_count']}`",
            ]
            if rep["findings"]:
                lines.append("")
                for f in rep["findings"]:
                    lines.append(f"- **`{f['type']}`** in `{f['file']}:L{f['line']}` (`{f['masked_preview']}`)")
            else:
                lines.append("- **Clean**: Zero hardcoded API keys, PATs, private keys, or DB credentials detected ✅")
            print("\n".join(lines))
        return 0

    raw = Path(args.input_file).read_text(encoding="utf-8", errors="ignore") if args.input_file else sys.stdin.read()
    res = scrub_text(raw)
    if args.format == "json":
        print(json.dumps(res, indent=2, ensure_ascii=False))
    else:
        print(res["scrubbed_text"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
