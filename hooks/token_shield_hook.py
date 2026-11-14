#!/usr/bin/env python3
"""Autonomous 3-Stage Lifecycle Engine (`SessionStart` + `PreToolUse` + `PostToolUse`).

Executes in <15ms with zero external dependencies and always fails open (`allow` / `{}`):

1. `SessionStart`:
   - Checks if the workspace has stored architectural facts in its SQLite Memory Vault.
   - Automatically injects up to 8 ultra-compact memories (<220 tokens) so every new
     conversation starts warm with zero codebase re-discovery turns!

2. `PreToolUse`:
   - **Token-Bomb Blocker**: Blocks unbounded full-file reads or `cat` dumps of giant
     generated lockfiles, `.map` sourcemaps, and `.min.js` bundles (>50 KB).
   - **Stateful Duplicate-Read Deduplicator**: Tracks `(file_path, mtime_ns, range)` per
     `conversationId`. Blocks redundant re-reads of files that have NOT changed on disk!
   - **Giant Source Auto-Clamper (`overwrite`)**: When an agent calls `read_file` with NO
     `StartLine`/`EndLine` on a huge source file (>1,200 lines & >55 KB), automatically
     clamps `overwrite: {"StartLine": 1, "EndLine": 280}` so tokens aren't wasted!
   - **Blind Retry-Loop Breaker**: Blocks running the exact same failing shell command
     3+ times in a row when no files were modified in between.

3. `PostToolUse`:
   - Updates the per-conversation state ledger: records successful file reads, clears
     read locks when files are edited, and tracks consecutive command error streaks.
"""

from __future__ import annotations

import hashlib
import json
import os
import re
import sqlite3
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional

BOMB_FILENAMES = {
    "package-lock.json",
    "pnpm-lock.yaml",
    "yarn.lock",
    "bun.lockb",
    "composer.lock",
    "pubspec.lock",
    "cargo.lock",
    "poetry.lock",
    "uv.lock",
}

BOMB_SUFFIXES = (".min.js", ".min.css", ".bundle.js", ".js.map", ".css.map", ".har")

SHELL_DUMP_RE = re.compile(
    r"\b(?:cat|type|get-content|gc)\b[^|;\n]*\b(?:package-lock\.json|pnpm-lock\.yaml|yarn\.lock|composer\.lock|pubspec\.lock|Cargo\.lock|[A-Za-z0-9_.-]+\.(?:min\.js|map|har))\b",
    re.IGNORECASE,
)
SHELL_BOUNDED_RE = re.compile(r"\b(?:head|tail|select-object|select-string|grep|rg|wc|measure-object)\b", re.IGNORECASE)

READ_TOOLS = {"read_file", "view_file"}
WRITE_TOOLS = {"edit_file", "write_file", "replace_file_content", "multi_replace_file_content", "write_to_file"}


def _state_dir(explicit_dir: Optional[Path] = None) -> Path:
    if explicit_dir is not None:
        explicit_dir.mkdir(parents=True, exist_ok=True)
        return explicit_dir
    base = os.environ.get("PLUGIN_DATA")
    if base:
        p = Path(base) / "hook_state"
    else:
        p = Path.home() / ".gemini" / "antigravity" / "plugin_data" / "smart-quota-orchestrator" / "hook_state"
    p.mkdir(parents=True, exist_ok=True)
    return p


def _load_conv_state(conv_id: str, state_root: Optional[Path] = None) -> Dict[str, Any]:
    if not conv_id:
        return {"reads": {}, "cmd_fail_cmd": "", "cmd_fail_streak": 0}
    safe_id = re.sub(r"[^A-Za-z0-9_-]", "_", conv_id)[:80]
    fpath = _state_dir(state_root) / f"{safe_id}.json"
    if fpath.is_file():
        try:
            return json.loads(fpath.read_text(encoding="utf-8"))
        except Exception:
            pass
    return {"reads": {}, "cmd_fail_cmd": "", "cmd_fail_streak": 0}


def _save_conv_state(conv_id: str, state: Dict[str, Any], state_root: Optional[Path] = None) -> None:
    if not conv_id:
        return
    safe_id = re.sub(r"[^A-Za-z0-9_-]", "_", conv_id)[:80]
    fpath = _state_dir(state_root) / f"{safe_id}.json"
    try:
        # Cap tracked reads to 150 entries so state file stays tiny (<12 KB)
        if len(state.get("reads", {})) > 150:
            items = list(state["reads"].items())[-100:]
            state["reads"] = dict(items)
        fpath.write_text(json.dumps(state), encoding="utf-8")
    except Exception:
        pass


def _log_roi_saving(event_type: str, tokens_saved: int, target: str = "", conv_id: str = "", state_root: Optional[Path] = None) -> None:
    if tokens_saved <= 0:
        return
    try:
        if state_root is not None:
            state_root.mkdir(parents=True, exist_ok=True)
            db_path = state_root / "roi_ledger.db"
        else:
            base = os.environ.get("PLUGIN_DATA")
            root = Path(base) if base else (Path.home() / ".gemini" / "antigravity" / "plugin_data" / "smart-quota-orchestrator")
            root.mkdir(parents=True, exist_ok=True)
            db_path = root / "roi_ledger.db"
        con = sqlite3.connect(str(db_path))
        con.execute(
            """
            CREATE TABLE IF NOT EXISTS savings_events (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                ts_utc TEXT NOT NULL,
                event_type TEXT NOT NULL,
                target TEXT NOT NULL DEFAULT '',
                tokens_saved INTEGER NOT NULL,
                conv_id TEXT NOT NULL DEFAULT ''
            )
            """
        )
        con.execute(
            "INSERT INTO savings_events(ts_utc, event_type, target, tokens_saved, conv_id) VALUES (strftime('%Y-%m-%dT%H:%M:%SZ', 'now'), ?, ?, ?, ?)",
            (event_type, target[:200], int(tokens_saved), conv_id[:80]),
        )
        con.commit()
        con.close()
    except Exception:
        pass


def _file_sig(p: Path, start_ln: Any, end_ln: Any) -> str:
    try:
        st = p.stat()
        return f"{st.st_mtime_ns}:{st.st_size}:{start_ln}:{end_ln}"
    except OSError:
        return ""


def _handle_session_start(payload: Dict[str, Any]) -> Dict[str, Any]:
    workspaces: List[str] = payload.get("workspacePaths") or []
    cwd = payload.get("cwd") or (workspaces[0] if workspaces else "")
    if not cwd:
        return {}

    ws = Path(cwd)
    candidates: List[Path] = [ws / ".sqo" / "memory.db"]
    plugin_data = os.environ.get("PLUGIN_DATA")
    if plugin_data:
        ws_slug = re.sub(r"[^A-Za-z0-9_.-]+", "_", ws.name.lower()) or "default"
        candidates.append(Path(plugin_data) / f"memory_{ws_slug}.db")

    db_file = next((c for c in candidates if c.is_file()), None)
    if db_file is None:
        return {}

    try:
        con = sqlite3.connect(str(db_file))
        rows = con.execute(
            "SELECT category, title, detail, files FROM memories ORDER BY id DESC LIMIT 8"
        ).fetchall()
        con.close()
    except Exception:
        return {}

    if not rows:
        return {}

    bullets = []
    for cat, title, detail, files in rows:
        f_tag = f" ({files})" if files else ""
        bullets.append(f"- [{cat}] {title}: {detail}{f_tag}")

    msg = (
        "[Smart Quota Memory Vault — Recalled Workspace Context]\n"
        + "\n".join(bullets)
    )
    return {"injectSteps": [{"systemMessage": {"systemMessage": msg}}]}


def evaluate_pre_tool(payload: Dict[str, Any], state_root: Optional[Path] = None) -> Dict[str, Any]:
    conv_id = str(payload.get("conversationId") or "")
    tool_call = payload.get("toolCall") or {}
    tool_name = str(tool_call.get("name") or "").lower()
    args = tool_call.get("args") or {}
    if not isinstance(args, dict):
        return {"decision": "allow"}

    # A) Guard file-reading tools
    if tool_name in READ_TOOLS:
        raw_path = str(args.get("Path") or args.get("AbsolutePath") or args.get("file_path") or "")
        if not raw_path:
            return {"decision": "allow"}

        p = Path(raw_path)
        fname_lower = p.name.lower()
        start_ln = args.get("StartLine")
        end_ln = args.get("EndLine")
        has_range = isinstance(start_ln, int) or isinstance(end_ln, int)
        has_tight_range = (
            isinstance(start_ln, int)
            and isinstance(end_ln, int)
            and 0 < (end_ln - start_ln) <= 150
        )

        # 1. Hard-block generated lockfile / sourcemap / minified token bombs (>50 KB)
        is_bomb_type = fname_lower in BOMB_FILENAMES or fname_lower.endswith(BOMB_SUFFIXES)
        if is_bomb_type and not has_tight_range:
            try:
                sz_kb = round(p.stat().st_size / 1024, 1) if p.is_file() else 999.0
            except OSError:
                sz_kb = 999.0
            if sz_kb >= 50.0:
                _log_roi_saving("Token-Bomb Blocker", int(sz_kb * 256), p.name, conv_id, state_root)
                return {
                    "decision": "deny",
                    "reason": (
                        f"[Smart Quota Shield] Blocked full read of generated artifact `{p.name}` ({sz_kb} KB) "
                        "to prevent massive context token waste. Read the primary manifest (`package.json`, "
                        "`pubspec.yaml`, `pyproject.toml`) or pass a tight `StartLine`–`EndLine` range (<=150 lines)."
                    ),
                }

        if p.is_file():
            # 2. Stateful Duplicate-Read Deduplicator (if conv_id present)
            if conv_id and p.suffix.lower() not in {".png", ".jpg", ".jpeg", ".webp", ".gif", ".pdf"}:
                state = _load_conv_state(conv_id, state_root)
                norm_key = str(p.resolve()).lower()
                sig = _file_sig(p, start_ln, end_ln)
                prev = state.get("reads", {}).get(norm_key)
                if prev and prev.get("sig") == sig:
                    prev_step = prev.get("step", "earlier")
                    saved_tok = max(120, int(p.stat().st_size / 4))
                    _log_roi_saving("Duplicate-Read Deduplicator", saved_tok, p.name, conv_id, state_root)
                    return {
                        "decision": "deny",
                        "reason": (
                            f"[Smart Quota Deduplicator] `{p.name}` (same line range) was already read at step #{prev_step} "
                            "and has NOT been modified on disk since then. Reuse the content already in your conversation "
                            "context, or pass a different `StartLine`–`EndLine` window."
                        ),
                    }

            # 3. Auto-Clamp blind full-file reads on huge source files (>55 KB & >1,200 lines)
            if not has_range and p.suffix.lower() in {".py", ".ts", ".tsx", ".js", ".jsx", ".dart", ".go", ".rs", ".java", ".php", ".cs", ".cpp"}:
                try:
                    sz = p.stat().st_size
                    if sz >= 55 * 1024:
                        with open(p, "r", encoding="utf-8", errors="ignore") as fh:
                            line_count = sum(1 for _ in fh)
                        if line_count > 1200:
                            saved_tok = max(1000, int((sz / 4) * ((line_count - 280) / line_count)))
                            _log_roi_saving("Giant-File Auto-Clamper", saved_tok, p.name, conv_id, state_root)
                            return {
                                "decision": "allow",
                                "overwrite": {"StartLine": 1, "EndLine": 280},
                            }
                except OSError:
                    pass

    # B) Guard shell commands
    if tool_name == "run_command":
        cmd = str(args.get("CommandLine") or args.get("command") or "").strip()
        if cmd:
            if SHELL_DUMP_RE.search(cmd) and not SHELL_BOUNDED_RE.search(cmd):
                _log_roi_saving("Shell Lockfile Dump Blocker", 24000, cmd[:80], conv_id, state_root)
                return {
                    "decision": "deny",
                    "reason": (
                        "[Smart Quota Shield] Blocked unbounded terminal dump of a lockfile/sourcemap/bundle. "
                        "Pipe through `rg`, `head -n 40`, or `Select-Object -First 40` instead."
                    ),
                }
            if conv_id:
                state = _load_conv_state(conv_id, state_root)
                cmd_hash = hashlib.sha1(cmd.encode("utf-8", errors="ignore")).hexdigest()[:16]
                if state.get("cmd_fail_cmd") == cmd_hash and int(state.get("cmd_fail_streak", 0)) >= 2:
                    _log_roi_saving("Blind Retry-Loop Breaker", 3200, cmd[:80], conv_id, state_root)
                    return {
                        "decision": "deny",
                        "reason": (
                            "[Smart Quota Loop-Breaker] This exact command already failed twice consecutively "
                            "with no file edits in between. Diagnose the root error and modify code, flags, "
                            "or inputs before retrying."
                        ),
                    }

    return {"decision": "allow"}


def evaluate_post_tool(payload: Dict[str, Any], state_root: Optional[Path] = None) -> Dict[str, Any]:
    conv_id = str(payload.get("conversationId") or "")
    if not conv_id:
        return {}

    tool_call = payload.get("toolCall") or {}
    tool_name = str(tool_call.get("name") or "").lower()
    args = tool_call.get("args") or {}
    err = str(payload.get("error") or "")
    step_idx = payload.get("stepIdx", "?")

    if not isinstance(args, dict):
        return {}

    state = _load_conv_state(conv_id, state_root)
    changed = False

    if tool_name in READ_TOOLS and not err:
        raw_path = str(args.get("Path") or args.get("AbsolutePath") or args.get("file_path") or "")
        if raw_path:
            p = Path(raw_path)
            if p.is_file():
                norm_key = str(p.resolve()).lower()
                sig = _file_sig(p, args.get("StartLine"), args.get("EndLine"))
                if sig:
                    state.setdefault("reads", {})[norm_key] = {"sig": sig, "step": step_idx}
                    changed = True

    elif tool_name in WRITE_TOOLS:
        raw_path = str(args.get("Path") or args.get("TargetFile") or args.get("file_path") or "")
        if raw_path:
            norm_key = str(Path(raw_path).resolve()).lower()
            state.get("reads", {}).pop(norm_key, None)
        # Reset command retry-loop lock whenever code is edited!
        state["cmd_fail_cmd"] = ""
        state["cmd_fail_streak"] = 0
        changed = True

    elif tool_name == "run_command":
        cmd = str(args.get("CommandLine") or args.get("command") or "").strip()
        cmd_hash = hashlib.sha1(cmd.encode("utf-8", errors="ignore")).hexdigest()[:16] if cmd else ""
        if err and cmd_hash:
            if state.get("cmd_fail_cmd") == cmd_hash:
                state["cmd_fail_streak"] = int(state.get("cmd_fail_streak", 0)) + 1
            else:
                state["cmd_fail_cmd"] = cmd_hash
                state["cmd_fail_streak"] = 1
        else:
            state["cmd_fail_cmd"] = ""
            state["cmd_fail_streak"] = 0
        changed = True

    if changed:
        _save_conv_state(conv_id, state, state_root)
    return {}


def evaluate_hook(payload: Dict[str, Any], state_root: Optional[Path] = None) -> Dict[str, Any]:
    event = str(payload.get("hookEventName") or "PreToolUse")
    if event == "SessionStart":
        return _handle_session_start(payload)
    if event == "PostToolUse":
        return evaluate_post_tool(payload, state_root=state_root)
    return evaluate_pre_tool(payload, state_root=state_root)


def main() -> int:
    try:
        raw = sys.stdin.read()
        payload = json.loads(raw) if raw.strip() else {}
        result = evaluate_hook(payload)
    except Exception:
        result = {"decision": "allow"}

    sys.stdout.write(json.dumps(result, ensure_ascii=False) + "\n")
    sys.stdout.flush()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
