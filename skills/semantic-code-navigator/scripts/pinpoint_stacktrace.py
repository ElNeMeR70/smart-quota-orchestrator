#!/usr/bin/env python3
"""One-Shot Multi-File Stack-Trace Pinpointer (`sqo pinpoint`).

When a test or server crashes with a multi-file stack trace (Python Traceback,
Node/TypeScript V8 stack, Dart/Flutter exception, Go panic, Rust backtrace, or PHP),
agents normally waste 5-8 turns opening each file sequentially!

`pinpoint_stacktrace.py` parses every `file:line` frame belonging to the user's
workspace (skipping `node_modules`, `.venv`, and language stdlibs) and extracts
the exact `±context` source window around EVERY frame in ONE compact payload!

Zero external dependencies (Python 3.8+ stdlib only).
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any, Dict, List, Set, Tuple

# Universal frame patterns: Python `File "x.py", line 42`, V8/TS/Dart/Go/Rust `path/file.ts:42:10`
PY_FRAME_RE = re.compile(r'File "([^"]+\.py)", line (\d+)')
COLON_FRAME_RE = re.compile(r"(?:at\s+[^\n(]*\(|-->\s+|\b)([A-Za-z0-9_./\\:-]+\.(?:ts|tsx|js|jsx|mjs|py|dart|go|rs|php|java|kt|rb|cs)):(\d+)(?::\d+)?")

EXTERNAL_NOISE = ("node_modules", ".venv", "venv", "site-packages", "dart-sdk", "flutter/packages", "internal/modules", "node:internal", "/usr/lib/")


def _configure_utf8() -> None:
    for stream in (sys.stdout, sys.stderr):
        if hasattr(stream, "reconfigure"):
            try:
                stream.reconfigure(encoding="utf-8")
            except Exception:
                pass


def _resolve_workspace_file(workspace: Path, raw_ref: str) -> Path | None:
    cleaned = raw_ref.strip().lstrip("file:///")
    if any(noise in cleaned.replace("\\", "/") for noise in EXTERNAL_NOISE):
        return None

    direct = Path(cleaned)
    if direct.is_file():
        try:
            direct.resolve().relative_to(workspace.resolve())
            return direct.resolve()
        except ValueError:
            pass

    cand = (workspace / cleaned).resolve()
    if cand.is_file():
        return cand

    # Suffix lookup for container paths like `/app/src/auth.ts` -> `<workspace>/src/auth.ts`
    norm = cleaned.replace("\\", "/")
    parts = [p for p in norm.split("/") if p and p not in {".", "..", "app", "workspace", "code"}]
    for idx in range(len(parts)):
        probe = (workspace / "/".join(parts[idx:])).resolve()
        if probe.is_file():
            return probe
    return None


def pinpoint_trace(workspace: Path, trace_text: str, radius: int = 10, max_frames: int = 6) -> Dict[str, Any]:
    raw_hits: List[Tuple[str, int]] = []
    for m in PY_FRAME_RE.finditer(trace_text):
        raw_hits.append((m.group(1), int(m.group(2))))
    for m in COLON_FRAME_RE.finditer(trace_text):
        raw_hits.append((m.group(1), int(m.group(2))))

    seen: Set[Tuple[Path, int]] = set()
    resolved_frames: List[Dict[str, Any]] = []

    # Reverse order puts the innermost crash site FIRST!
    for raw_path, line_no in reversed(raw_hits):
        fpath = _resolve_workspace_file(workspace, raw_path)
        if fpath is None or (fpath, line_no) in seen:
            continue
        seen.add((fpath, line_no))
        try:
            lines = fpath.read_text(encoding="utf-8", errors="ignore").splitlines()
        except OSError:
            continue

        start = max(1, line_no - radius)
        end = min(len(lines), line_no + radius)
        snippet_lines = []
        for ln in range(start, end + 1):
            marker = ">>" if ln == line_no else "  "
            snippet_lines.append(f"{marker} {ln:4d} | {lines[ln - 1]}")

        rel = str(fpath.relative_to(workspace.resolve())).replace("\\", "/")
        resolved_frames.append({
            "file": rel,
            "crash_line": line_no,
            "window": f"L{start}-L{end}",
            "full_file_lines": len(lines),
            "snippet": "\n".join(snippet_lines),
        })
        if len(resolved_frames) >= max_frames:
            break

    # Extract concise error headline
    err_lines = [ln.strip() for ln in trace_text.splitlines() if re.search(r"(?:error|exception|panic|failed):", ln, re.I)]
    headline = err_lines[-1][:200] if err_lines else (trace_text.strip().splitlines()[-1][:200] if trace_text.strip() else "Unknown error")

    return {
        "error_headline": headline,
        "frames_extracted": len(resolved_frames),
        "frames": resolved_frames,
    }


def render_markdown(rep: Dict[str, Any]) -> str:
    lines = [
        "## Surgical Stack-Trace Code Pinpoint",
        f"- **Error Headline**: `{rep['error_headline']}`",
        f"- **Workspace Frames Extracted**: `{rep['frames_extracted']}` *(innermost crash site first)*",
        "",
    ]
    if not rep["frames"]:
        lines.append("_No local workspace file frames matched in stack trace._")
        return "\n".join(lines)

    for idx, fr in enumerate(rep["frames"], start=1):
        lines.append(
            f"### Frame {idx}: `{fr['file']}:L{fr['crash_line']}` *(Window `{fr['window']}` of `{fr['full_file_lines']}` lines)*"
        )
        lines.append(f"```text\n{fr['snippet']}\n```")
    return "\n".join(lines)


def main() -> int:
    _configure_utf8()
    parser = argparse.ArgumentParser(description="Extract exact multi-file source windows from any crash stack trace in 1 step.")
    parser.add_argument("--workspace", "-w", default=".", help="Workspace root directory.")
    parser.add_argument("--trace-file", "-f", help="Path to crash log / traceback file (or pipe via stdin).")
    parser.add_argument("--radius", "-r", type=int, default=10, help="Lines of context above/below crash line (default: 10).")
    parser.add_argument("--format", choices=("markdown", "json"), default="markdown", help="Output format.")
    args = parser.parse_args()

    raw = Path(args.trace_file).read_text(encoding="utf-8", errors="ignore") if args.trace_file else sys.stdin.read()
    rep = pinpoint_trace(Path(args.workspace).resolve(), raw, radius=max(3, args.radius))
    if args.format == "json":
        print(json.dumps(rep, indent=2, ensure_ascii=False))
    else:
        print(render_markdown(rep))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
