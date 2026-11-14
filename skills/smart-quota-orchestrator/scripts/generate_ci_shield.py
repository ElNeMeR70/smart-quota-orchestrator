#!/usr/bin/env python3
"""GitHub Actions PR Token & Architecture Shield Generator (`sqo ci-shield` / `sqo_ci_shield`).

Generates `.github/workflows/sqo-shield.yml` for ANY repository so every Pull Request automatically
verifies:
  1. Zero Leaked Secrets (`scrub_secrets.py`)
  2. Pre-Flight Syntax, Balanced Delimiters & Conflict Markers (`shadow_dry_run.py`)
  3. Prompt-Tax Overhead & 90% LLM KV-Cache Stability (`audit_cache_stability.py`)
  4. Oversized 4K Vision Media Token Audit (`estimate_media_tokens.py`)
and publishes a clean Markdown summary directly into `$GITHUB_STEP_SUMMARY`!
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any, Dict

WORKFLOW_TEMPLATE = """name: ⚡ Smart Quota & Architecture PR Shield

on:
  pull_request:
    branches: [ main, master, develop ]
  workflow_dispatch:

permissions:
  contents: read

jobs:
  sqo-pr-shield:
    name: 🛡️ AI Quota, Secret & Syntax Shield
    runs-on: ubuntu-latest
    steps:
      - name: Checkout Repository
        uses: actions/checkout@v4

      - name: Set up Python 3.11 (Zero External Dependencies)
        uses: actions/setup-python@v5
        with:
          python-version: "3.11"

      - name: Fetch Smart Quota & Swarm Orchestrator Engine
        run: |
          git clone --depth 1 https://github.com/ElNeMeR70/smart-quota-orchestrator.git /tmp/sqo

      - name: Run Pre-Flight Syntax, Secret, KV-Cache & Media Shield
        run: |
          {
            echo "## ⚡ Smart Quota OS — Pull Request Shield Report"
            echo "> Powered by [Smart Quota & Swarm Orchestrator](https://sqo.elnemer-ai.com)"
            echo ""
            python /tmp/sqo/sqo.py dry-run --workspace . .
            echo ""
            python /tmp/sqo/sqo.py cache-audit --workspace .
            echo ""
            python /tmp/sqo/sqo.py media --workspace .
          } >> "$GITHUB_STEP_SUMMARY"

      - name: Enforce Zero Secret Leaks & Clean Syntax
        run: |
          python /tmp/sqo/sqo.py scrub --workspace .
          python /tmp/sqo/sqo.py dry-run --workspace . .
"""


def install_ci_shield(workspace: Path, overwrite: bool = True) -> Dict[str, Any]:
    ws = workspace.resolve()
    wf_path = ws / ".github" / "workflows" / "sqo-shield.yml"
    wf_path.parent.mkdir(parents=True, exist_ok=True)
    if wf_path.is_file() and not overwrite:
        return {"installed": False, "path": str(wf_path), "reason": "already_exists"}
    wf_path.write_text(WORKFLOW_TEMPLATE, encoding="utf-8")
    return {"installed": True, "path": str(wf_path)}


def main() -> int:
    for s in (sys.stdout, sys.stderr):
        if hasattr(s, "reconfigure"):
            try:
                s.reconfigure(encoding="utf-8")
            except Exception:
                pass
    parser = argparse.ArgumentParser(description="Generate GitHub Actions PR Token & Architecture Shield workflow.")
    parser.add_argument("--workspace", "-w", default=".", help="Target repository root.")
    args = parser.parse_args()

    res = install_ci_shield(Path(args.workspace))
    print(json.dumps(res, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
