#!/usr/bin/env python3
"""Universal 6-IDE Configuration & Ignore-Shield Synchronizer (`sqo sync-ide`).

Wires a target workspace so Smart Quota & Swarm Orchestrator's MCP Server (`sqo-engine`)
and Context-Bomb Ignore Shield work seamlessly across ALL major AI coding tools:
  1. Google Antigravity (`.agentignore`)
  2. Cursor (`.cursor/mcp.json` + `.cursorignore`)
  3. Claude Code (`.mcp.json` + `.claudeignore`)
  4. VS Code / GitHub Copilot (`.vscode/mcp.json`)
  5. Windsurf (`.codeiumignore`)

Safely merges into existing JSON files without overwriting unrelated MCP servers!
Zero external dependencies (Python 3.8+ stdlib only).
"""

from __future__ import annotations

import argparse
import importlib.util
import json
import sys
from pathlib import Path
from typing import Any, Dict, List


def _configure_utf8() -> None:
    for stream in (sys.stdout, sys.stderr):
        if hasattr(stream, "reconfigure"):
            try:
                stream.reconfigure(encoding="utf-8")
            except Exception:
                pass


def _merge_mcp_json(target_file: Path, root_key: str, server_name: str, server_cfg: Dict[str, Any], dry_run: bool) -> str:
    existing: Dict[str, Any] = {}
    if target_file.is_file():
        try:
            existing = json.loads(target_file.read_text(encoding="utf-8"))
        except Exception:
            existing = {}

    existing.setdefault(root_key, {})[server_name] = server_cfg
    if not dry_run:
        target_file.parent.mkdir(parents=True, exist_ok=True)
        target_file.write_text(json.dumps(existing, indent=2) + "\n", encoding="utf-8")
    return str(target_file).replace("\\", "/")


def sync_workspace_ides(
    workspace: Path,
    suite_root: Path,
    targets: List[str],
    dry_run: bool = False,
) -> Dict[str, Any]:
    mcp_script = str((suite_root / "mcp_server.py").resolve()).replace("\\", "/")
    stdio_cfg = {"command": "python", "args": [mcp_script]}

    ign_script = suite_root / "skills" / "context-compactor" / "scripts" / "generate_agent_ignore.py"
    spec = importlib.util.spec_from_file_location("ign", ign_script)
    assert spec and spec.loader
    ign_mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(ign_mod)
    ignore_content: str = ign_mod.scan_token_bombs(workspace)["generated_ignore_content"]

    synced_files: List[str] = []
    chosen = {t.lower() for t in targets}
    if "all" in chosen:
        chosen = {"antigravity", "cursor", "claude", "vscode", "windsurf"}

    def write_ignore(fname: str) -> None:
        p = workspace / fname
        if not dry_run:
            p.write_text(ignore_content, encoding="utf-8")
        synced_files.append(str(p).replace("\\", "/"))

    if "antigravity" in chosen:
        write_ignore(".agentignore")

    if "cursor" in chosen:
        write_ignore(".cursorignore")
        synced_files.append(_merge_mcp_json(workspace / ".cursor" / "mcp.json", "mcpServers", "sqo-engine", stdio_cfg, dry_run))

    if "claude" in chosen:
        write_ignore(".claudeignore")
        synced_files.append(_merge_mcp_json(workspace / ".mcp.json", "mcpServers", "sqo-engine", stdio_cfg, dry_run))

    if "vscode" in chosen:
        synced_files.append(
            _merge_mcp_json(
                workspace / ".vscode" / "mcp.json",
                "servers",
                "sqo-engine",
                {"type": "stdio", **stdio_cfg},
                dry_run,
            )
        )

    if "windsurf" in chosen:
        write_ignore(".codeiumignore")

    return {
        "workspace": str(workspace).replace("\\", "/"),
        "dry_run": dry_run,
        "mcp_server_wired": mcp_script,
        "synced_files": synced_files,
    }


def main() -> int:
    _configure_utf8()
    parser = argparse.ArgumentParser(description="Wire sqo-engine MCP server and ignore shields across Antigravity, Cursor, Claude Code, VS Code & Windsurf.")
    parser.add_argument("--workspace", "-w", default=".", help="Target project workspace to configure.")
    parser.add_argument(
        "--ides",
        nargs="+",
        default=["all"],
        choices=("all", "antigravity", "cursor", "claude", "vscode", "windsurf"),
        help="IDEs to configure (default: all).",
    )
    parser.add_argument("--dry-run", action="store_true", help="Preview files without writing.")
    parser.add_argument("--format", choices=("markdown", "json"), default="markdown", help="Output format.")
    args = parser.parse_args()

    suite_root = Path(__file__).resolve().parents[3]
    res = sync_workspace_ides(Path(args.workspace).resolve(), suite_root, args.ides, dry_run=args.dry_run)
    if args.format == "json":
        print(json.dumps(res, indent=2, ensure_ascii=False))
    else:
        mode = "(DRY RUN)" if res["dry_run"] else "✅"
        lines = [f"## Cross-IDE Quota Shield & MCP Sync {mode}", ""]
        for f in res["synced_files"]:
            lines.append(f"- `{f}`")
        print("\n".join(lines))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
