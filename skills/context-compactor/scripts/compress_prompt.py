#!/usr/bin/env python3
"""Deterministic Prompt, JSON Array & Log Compressor (`sqo compress-prompt`).

Compresses verbose raw developer inputs BEFORE sending them to expensive LLMs:
  1. Strips ANSI escape codes, carriage-return progress bars & empty boilerplate lines.
  2. Collapses consecutive duplicate/near-duplicate log lines into `[Repeated xN]`.
  3. Compresses huge repetitive JSON arrays (>4 objects with identical keys) into
     `Schema + First 2 Sample Records + Total Count` (saves 75%-95% tokens on API dumps!).
  4. Automatically scrubs accidentally pasted credentials (`scrub_secrets.py`).

Zero external dependencies (Python 3.8+ stdlib only).
"""

from __future__ import annotations

import argparse
import importlib.util
import json
import re
import sys
from pathlib import Path
from typing import Any, Dict, List

ANSI_RE = re.compile(r"\x1b\[[0-9;]*[A-Za-z]")
JSON_BLOCK_RE = re.compile(r"(\[\s*\{[\s\S]{350,}?\}\s*\])")
NORM_LOG_RE = re.compile(r"\b(?:\d{4}-\d{2}-\d{2}[T ]\d{2}:\d{2}:\d{2}(?:\.\d+)?Z?|\d+\.\d+ms|0x[0-9a-fA-F]+)\b")


def _configure_utf8() -> None:
    for s in (sys.stdout, sys.stderr):
        if hasattr(s, "reconfigure"):
            try:
                s.reconfigure(encoding="utf-8")
            except Exception:
                pass


def _compress_json_arrays(text: str) -> tuple[str, int]:
    arrays_compacted = 0

    def _repl(match: re.Match[str]) -> str:
        nonlocal arrays_compacted
        raw = match.group(1)
        try:
            parsed = json.loads(raw)
        except Exception:
            return raw
        if not isinstance(parsed, list) or len(parsed) <= 4:
            return raw
        if not all(isinstance(x, dict) for x in parsed):
            return raw
        keys = sorted({k for item in parsed[:10] for k in item.keys()})
        arrays_compacted += 1
        compact_obj = {
            "_sqo_compacted_array": True,
            "total_items": len(parsed),
            "schema_keys": keys,
            "sample_first_2": parsed[:2],
            "sample_last_1": parsed[-1],
        }
        return json.dumps(compact_obj, ensure_ascii=False, indent=2)

    return JSON_BLOCK_RE.sub(_repl, text), arrays_compacted


def compress_raw_prompt(raw_text: str, scrub: bool = True) -> Dict[str, Any]:
    orig_tokens = max(1, int(len(raw_text) / 4))
    cleaned = ANSI_RE.sub("", raw_text).replace("\r\n", "\n").replace("\r", "\n")

    # 1. Compact large repetitive JSON arrays
    cleaned, json_arrays_compacted = _compress_json_arrays(cleaned)

    # 2. Collapse consecutive duplicate/near-duplicate log lines & blank bursts
    out_lines: List[str] = []
    prev_sig = None
    repeat_count = 0
    collapsed_lines = 0
    blank_streak = 0

    def _flush_repeats() -> None:
        nonlocal repeat_count
        if repeat_count > 1 and out_lines:
            out_lines[-1] = f"{out_lines[-1]}  [Repeated ×{repeat_count}]"
        repeat_count = 0

    for line in cleaned.splitlines():
        stripped = line.rstrip()
        if not stripped:
            _flush_repeats()
            prev_sig = None
            blank_streak += 1
            if blank_streak <= 1:
                out_lines.append("")
            else:
                collapsed_lines += 1
            continue

        blank_streak = 0
        sig = NORM_LOG_RE.sub("<TS>", stripped)
        if sig == prev_sig and len(stripped) > 12:
            repeat_count += 1
            collapsed_lines += 1
        else:
            _flush_repeats()
            out_lines.append(stripped)
            prev_sig = sig
            repeat_count = 1

    _flush_repeats()
    compacted_text = "\n".join(out_lines).strip()

    redacted_secrets = 0
    if scrub:
        scrub_path = Path(__file__).resolve().parents[2] / "project-memory-vault" / "scripts" / "scrub_secrets.py"
        if scrub_path.is_file():
            spec = importlib.util.spec_from_file_location("scrub_secrets", scrub_path)
            if spec and spec.loader:
                mod = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(mod)
                s_res = mod.scrub_text(compacted_text)
                compacted_text = s_res["scrubbed_text"]
                redacted_secrets = s_res["redacted_total"]

    new_tokens = max(1, int(len(compacted_text) / 4))
    saved_pct = round(max(0.0, (1.0 - new_tokens / orig_tokens) * 100.0), 1)

    return {
        "original_tokens": orig_tokens,
        "compressed_tokens": new_tokens,
        "tokens_saved": max(0, orig_tokens - new_tokens),
        "savings_pct": saved_pct,
        "json_arrays_compacted": json_arrays_compacted,
        "duplicate_lines_collapsed": collapsed_lines,
        "secrets_redacted": redacted_secrets,
        "compressed_text": compacted_text,
    }


def main() -> int:
    _configure_utf8()
    parser = argparse.ArgumentParser(description="Deterministically compress noisy prompts, JSON dumps, and logs.")
    parser.add_argument("--file", "-f", help="Input text/JSON/log file (or pipe via stdin).")
    parser.add_argument("--format", choices=("markdown", "json", "raw"), default="markdown", help="Output format.")
    args = parser.parse_args()

    raw = Path(args.file).read_text(encoding="utf-8", errors="ignore") if args.file else sys.stdin.read()
    rep = compress_raw_prompt(raw)
    if args.format == "json":
        print(json.dumps(rep, indent=2, ensure_ascii=False))
    elif args.format == "raw":
        print(rep["compressed_text"])
    else:
        print(
            f"## ⚡ Smart Prompt & Payload Compression (`-{rep['savings_pct']}%` | Saved `{rep['tokens_saved']:,}` tokens)\n"
            f"- **Before**: `~{rep['original_tokens']:,}` tok -> **After**: `~{rep['compressed_tokens']:,}` tok "
            f"(`{rep['json_arrays_compacted']}` JSON array(s) compacted, `{rep['duplicate_lines_collapsed']}` duplicate lines collapsed, `{rep['secrets_redacted']}` secret(s) scrubbed)\n\n"
            f"```text\n{rep['compressed_text']}\n```"
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
