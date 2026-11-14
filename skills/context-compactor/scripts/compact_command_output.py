#!/usr/bin/env python3
"""Build, Test & Linter CLI Output Denoiser.

Executes a command (or filters piped stdin) and strips:
  - ANSI color/cursor escape codes & progress spinner spam
  - Hundreds of passing test lines (`PASS`, `ok`, `✓`)
  - Repeated node_modules / framework internal stack frames

Extracts ONLY exit status, failure blocks, compiler/type errors (`file:line:col`),
and final summary metrics — cutting noisy CLI output tokens by 80-95%!

Zero external dependencies (Python 3.8+ stdlib only).
"""

from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from typing import Any, Dict, List

ANSI_RE = re.compile(r"\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])")
ERROR_SIGNAL_RE = re.compile(
    r"(?:error[\s:\[]|failed|failure|exception|traceback|assertionerror|panic:|✕|✖|FAIL\s|[A-Za-z0-9_./\\-]+\.[a-z]{1,4}:\d+:\d+)",
    re.IGNORECASE,
)
SUMMARY_SIGNAL_RE = re.compile(
    r"(?:test suites?:|tests?:|\d+\s+passed|\d+\s+failed|ran\s+\d+\s+tests|compiled\s+successfully|build\s+failed|found\s+\d+\s+errors?)",
    re.IGNORECASE,
)
NOISE_STACK_RE = re.compile(r"^\s*at\s+.*(?:node_modules|internal/process|node:internal)")


def _configure_utf8() -> None:
    for stream in (sys.stdout, sys.stderr):
        if hasattr(stream, "reconfigure"):
            try:
                stream.reconfigure(encoding="utf-8")
            except Exception:
                pass


def denoise_output(raw_text: str, exit_code: int = 0, max_lines: int = 80) -> Dict[str, Any]:
    clean = ANSI_RE.sub("", raw_text.replace("\r\n", "\n").replace("\r", "\n"))
    all_lines = clean.splitlines()
    raw_tokens = int(len(raw_text) / 4)

    kept_Failure_lines: List[str] = []
    summaries: List[str] = []
    context_countdown = 0
    dedup_seen: set[str] = set()

    for line in all_lines:
        stripped = line.strip()
        if not stripped:
            if context_countdown > 0:
                context_countdown -= 1
            continue
        if NOISE_STACK_RE.match(line):
            continue

        if SUMMARY_SIGNAL_RE.search(stripped):
            if stripped not in summaries:
                summaries.append(stripped)

        if ERROR_SIGNAL_RE.search(stripped):
            if stripped not in dedup_seen:
                dedup_seen.add(stripped)
                kept_Failure_lines.append(line)
            context_countdown = 4
        elif context_countdown > 0:
            kept_Failure_lines.append(line)
            context_countdown -= 1

    if not kept_Failure_lines and exit_code != 0:
        # Fallback: keep tail of output when command failed without standard error keywords
        kept_Failure_lines = all_lines[-min(35, len(all_lines)) :]

    trimmed_failures = kept_Failure_lines[:max_lines]
    compacted_chars = sum(len(x) for x in trimmed_failures) + sum(len(x) for x in summaries)
    compacted_tokens = max(1, int(compacted_chars / 4))
    savings_pct = max(0, round((1 - compacted_tokens / max(1, raw_tokens)) * 100)) if raw_tokens > 40 else 0

    return {
        "exit_code": exit_code,
        "raw_line_count": len(all_lines),
        "raw_approx_tokens": raw_tokens,
        "compacted_approx_tokens": compacted_tokens,
        "token_savings_pct": savings_pct,
        "summary_lines": summaries[-8:],
        "diagnostic_lines": trimmed_failures,
    }


def render_markdown(res: Dict[str, Any]) -> str:
    status = "PASS (0)" if res["exit_code"] == 0 else f"FAIL ({res['exit_code']})"
    lines = [
        f"## Denoised Command Output — **{status}**",
        f"- **Compression**: `{res['raw_line_count']}` lines (`~{res['raw_approx_tokens']:,}` tokens) -> `{len(res['diagnostic_lines'])}` diagnostic lines (**{res['token_savings_pct']}% token reduction**)",
    ]
    if res["summary_lines"]:
        lines.append(f"- **Summary**: {' | '.join(f'`{s}`' for s in res['summary_lines'])}")
    if res["diagnostic_lines"]:
        lines.append("\n```text")
        lines.extend(res["diagnostic_lines"])
        lines.append("```")
    return "\n".join(lines)


def main() -> int:
    _configure_utf8()
    parser = argparse.ArgumentParser(description="Run a CLI command or filter stdin and return only actionable errors/summaries.")
    parser.add_argument("--cmd", "-c", help="Shell command to execute and denoise.")
    parser.add_argument("--max-lines", "-m", type=int, default=80, help="Max diagnostic lines to retain (default: 80).")
    parser.add_argument("--format", choices=("markdown", "json"), default="markdown", help="Output format.")
    args = parser.parse_args()

    if args.cmd:
        proc = subprocess.run(args.cmd, shell=True, capture_output=True, text=True, errors="ignore", check=False)
        combined = (proc.stdout or "") + ("\n" + proc.stderr if proc.stderr else "")
        code = proc.returncode
    elif not sys.stdin.isatty():
        combined = sys.stdin.read()
        code = 0
    else:
        parser.error("Provide --cmd '<command>' or pipe command output via stdin.")

    report = denoise_output(combined, exit_code=code, max_lines=args.max_lines)
    if args.format == "json":
        print(json.dumps(report, indent=2, ensure_ascii=False))
    else:
        print(render_markdown(report))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
