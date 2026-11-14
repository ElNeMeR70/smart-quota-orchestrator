#!/usr/bin/env python3
"""Superpowers Isolated Sandbox Runner — Git Worktree + Pure-FS Fallback (v10.0 Apex).

Spins up zero-risk isolated sandboxes under `.sqo/sandboxes/<name>` so agents can
prototype risky refactors, run test commands safely, inspect diffs, and promote
verified files back to the main workspace or discard cleanly in 1 command!
"""

from __future__ import annotations

import argparse
import hashlib
import json
import shutil
import subprocess
from pathlib import Path
from typing import Any, Dict, List

SKIP_DIRS = {".git", "node_modules", ".venv", "venv", "__pycache__", "build", "dist", ".next", ".dart_tool", "vendor", ".sqo"}


def _sandbox_root(workspace: Path) -> Path:
    d = workspace.resolve() / ".sqo" / "sandboxes"
    d.mkdir(parents=True, exist_ok=True)
    return d


def _sha256_file(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


def create_sandbox(workspace: Path, name: str) -> Dict[str, Any]:
    workspace = workspace.resolve()
    safe_name = "".join(c for c in name if c.isalnum() or c in ("-", "_"))[:40] or "exp-1"
    dest = _sandbox_root(workspace) / safe_name
    if dest.exists():
        shutil.rmtree(dest, ignore_errors=True)

    # Try native git worktree if inside a committed git repository
    mode = "fs_snapshot"
    if (workspace / ".git").exists():
        try:
            proc = subprocess.run(
                ["git", "worktree", "add", "--detach", str(dest), "HEAD"],
                cwd=str(workspace),
                capture_output=True,
                text=True,
                timeout=12,
            )
            if proc.returncode == 0 and dest.is_dir():
                mode = "git_worktree"
        except Exception:
            pass

    if mode == "fs_snapshot":
        dest.mkdir(parents=True, exist_ok=True)
        copied = 0
        for item in workspace.rglob("*"):
            rel = item.relative_to(workspace)
            if any(part in SKIP_DIRS for part in rel.parts):
                continue
            if item.is_file() and item.stat().st_size <= 2 * 1024 * 1024:
                target = dest / rel
                target.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(item, target)
                copied += 1
        return {"ok": True, "name": safe_name, "mode": mode, "path": str(dest), "copied_files": copied}

    return {"ok": True, "name": safe_name, "mode": mode, "path": str(dest)}


def diff_sandbox(workspace: Path, name: str) -> Dict[str, Any]:
    workspace = workspace.resolve()
    sb = _sandbox_root(workspace) / name
    if not sb.is_dir():
        return {"ok": False, "error": f"Sandbox '{name}' does not exist."}

    modified: List[str] = []
    added: List[str] = []
    for item in sb.rglob("*"):
        if not item.is_file():
            continue
        rel = item.relative_to(sb)
        if any(part in SKIP_DIRS for part in rel.parts):
            continue
        rel_str = str(rel).replace("\\", "/")
        orig = workspace / rel
        if not orig.is_file():
            added.append(rel_str)
        elif _sha256_file(item) != _sha256_file(orig):
            modified.append(rel_str)

    return {"ok": True, "name": name, "modified": sorted(modified), "added": sorted(added)}


def promote_sandbox(workspace: Path, name: str) -> Dict[str, Any]:
    workspace = workspace.resolve()
    d = diff_sandbox(workspace, name)
    if not d.get("ok"):
        return d
    sb = _sandbox_root(workspace) / name
    promoted: List[str] = []
    for rel_str in d["modified"] + d["added"]:
        src = sb / rel_str
        dst = workspace / rel_str
        dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(src, dst)
        promoted.append(rel_str)
    return {"ok": True, "name": name, "promoted_files": promoted}


def cleanup_sandbox(workspace: Path, name: str) -> Dict[str, Any]:
    workspace = workspace.resolve()
    sb = _sandbox_root(workspace) / name
    if (workspace / ".git").exists():
        try:
            subprocess.run(["git", "worktree", "remove", "--force", str(sb)], cwd=str(workspace), capture_output=True, timeout=10)
        except Exception:
            pass
    if sb.exists():
        shutil.rmtree(sb, ignore_errors=True)
    return {"ok": True, "removed": name}


def list_sandboxes(workspace: Path) -> Dict[str, Any]:
    root = _sandbox_root(workspace)
    items = [p.name for p in sorted(root.iterdir()) if p.is_dir()]
    return {"ok": True, "sandboxes": items}


def main() -> int:
    ap = argparse.ArgumentParser(description="Isolated Experiment Sandbox Runner")
    ap.add_argument("action", choices=["create", "diff", "promote", "cleanup", "list"])
    ap.add_argument("--workspace", default=".")
    ap.add_argument("--name", default="exp-1")
    ns = ap.parse_args()

    ws = Path(ns.workspace).resolve()
    if ns.action == "create":
        out = create_sandbox(ws, ns.name)
    elif ns.action == "diff":
        out = diff_sandbox(ws, ns.name)
    elif ns.action == "promote":
        out = promote_sandbox(ws, ns.name)
    elif ns.action == "cleanup":
        out = cleanup_sandbox(ws, ns.name)
    else:
        out = list_sandboxes(ws)
    print(json.dumps(out, indent=2, ensure_ascii=False))
    return 0 if out.get("ok", True) else 1


if __name__ == "__main__":
    raise SystemExit(main())
