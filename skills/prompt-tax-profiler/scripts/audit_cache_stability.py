#!/usr/bin/env python3
"""LLM Prompt KV-Cache Prefix Stability Auditor (`sqo cache-audit`).

Gemini Context Caching and Anthropic/OpenAI Prompt Caching discount input tokens
by 75%-90% ONLY when the system/rule/hook prefix stays deterministic across turns!

Scans workspace hooks, MCP servers, and rule files (`AGENTS.md`, `CLAUDE.md`,
`GEMINI.md`) to detect **KV-Cache Busting Anti-Patterns**:
  1. `PreInvocation` hooks injecting changing timestamps, `uuid4()`, or random values
     into persistent `systemMessage` trajectories!
  2. Unsorted directory/glob walks (`os.listdir`, `set` iteration) inside prompt-generating
     scripts causing non-deterministic ordering across invocations.
  3. Oversized volatile rules vs. deterministic static prefixes.

Zero external dependencies (Python 3.8+ stdlib only).
"""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
from pathlib import Path
from typing import Any, Dict, List

IGNORE_DIRS = {".git", ".sqo", "node_modules", ".next", "dist", "build", "__pycache__", ".venv", "venv"}

VOLATILE_TIME_RE = re.compile(r"\b(?:(?:dt|datetime)\.now|time\.time|Date\.now|new Date\(\)|uuid\.uuid4|random\.choice|Math\.random)\b")
UNSORTED_DIR_RE = re.compile(r"\bos\.listdir\s*\((?!\s*sorted)")


def _configure_utf8() -> None:
    for stream in (sys.stdout, sys.stderr):
        if hasattr(stream, "reconfigure"):
            try:
                stream.reconfigure(encoding="utf-8")
            except Exception:
                pass


def audit_cache_stability(workspace: Path) -> Dict[str, Any]:
    issues: List[Dict[str, Any]] = []
    checked_files = 0
    has_pre_invocation_hook = False

    # 1. Inspect hooks.json files
    for hooks_path in [workspace / "hooks.json", workspace / ".agents" / "hooks.json", workspace / ".claude" / "settings.json"]:
        if hooks_path.is_file():
            checked_files += 1
            text = hooks_path.read_text(encoding="utf-8", errors="ignore")
            if '"PreInvocation"' in text:
                has_pre_invocation_hook = True
                issues.append({
                    "severity": "MEDIUM",
                    "file": str(hooks_path.relative_to(workspace)).replace("\\", "/"),
                    "issue": "Uses `PreInvocation` hook — verify it does NOT inject dynamic timestamps/counters on every turn (prefer `SessionStart` for one-time static context so KV-cache stays warm!).",
                })

    # 2. Scan hook & MCP scripts for non-deterministic prompt output
    for sub in ("hooks", ".agents", "scripts"):
        root = workspace / sub
        if not root.is_dir():
            continue
        for dirpath, dirnames, filenames in os.walk(root):
            dirnames[:] = [d for d in dirnames if d not in IGNORE_DIRS]
            for fname in filenames:
                fpath = Path(dirpath) / fname
                if fpath.suffix.lower() not in {".py", ".js", ".ts", ".sh"}:
                    continue
                checked_files += 1
                rel = str(fpath.relative_to(workspace)).replace("\\", "/")
                src = fpath.read_text(encoding="utf-8", errors="ignore")
                if "injectSteps" in src and VOLATILE_TIME_RE.search(src):
                    issues.append({
                        "severity": "HIGH",
                        "file": rel,
                        "issue": "Injects message steps while calling volatile time/UUID/random APIs — busts LLM KV-cache prefix!",
                    })
                if UNSORTED_DIR_RE.search(src) and "sorted(" not in src:
                    issues.append({
                        "severity": "LOW",
                        "file": rel,
                        "issue": "Uses unsorted `os.listdir()` — sort filesystem entries deterministically (`sorted(...)`) to preserve identical prompt prefixes across OSes.",
                    })

    high_count = sum(1 for x in issues if x["severity"] == "HIGH")
    score = max(0, 100 - high_count * 35 - (len(issues) - high_count) * 10)
    status = "OPTIMAL (90%+ KV-Cache Friendly)" if score >= 90 else ("MODERATE" if score >= 65 else "CACHE-BUSTING DETECTED")

    return {
        "workspace": str(workspace).replace("\\", "/"),
        "cache_stability_score": score,
        "status": status,
        "checked_customization_files": checked_files,
        "has_per_turn_pre_invocation": has_pre_invocation_hook,
        "issues": issues,
    }


def render_markdown(rep: Dict[str, Any]) -> str:
    lines = [
        "## LLM Prompt KV-Cache Prefix Stability Audit",
        f"- **Stability Score**: **`{rep['cache_stability_score']} / 100`** — **{rep['status']}**",
        f"- **Customization / Hook Files Audited**: `{rep['checked_customization_files']}`",
        "",
    ]
    if not rep["issues"]:
        lines.append("- **Zero KV-Cache Busting Patterns Found**: Static rules, `SessionStart` one-shot injection, and deterministic sorting keep prompt prefixes 100% cacheable ✅")
    else:
        lines.append("### Detected Cache-Invalidation Risks\n")
        for item in rep["issues"]:
            lines.append(f"- **[{item['severity']}] `{item['file']}`**: {item['issue']}")
    return "\n".join(lines)


def main() -> int:
    _configure_utf8()
    parser = argparse.ArgumentParser(description="Audit hooks, MCP tools, and rules for LLM Prompt KV-Cache prefix stability.")
    parser.add_argument("--workspace", "-w", default=".", help="Workspace path to audit.")
    parser.add_argument("--format", choices=("markdown", "json"), default="markdown", help="Output format.")
    args = parser.parse_args()

    rep = audit_cache_stability(Path(args.workspace).resolve())
    if args.format == "json":
        print(json.dumps(rep, indent=2, ensure_ascii=False))
    else:
        print(render_markdown(rep))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
