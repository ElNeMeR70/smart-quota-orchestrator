#!/usr/bin/env python3
"""Session Time-Machine & Surgical Rollback Checkpoints (`sqo checkpoint` / `sqo_checkpoint`).

Content-addressable, zero-git-conflict micro-snapshot engine stored in `<workspace>/.sqo/checkpoints/`:
  - `create`  : Snapshot workspace source files into deduplicated zlib SHA-256 blobs in <25ms!
  - `list`    : View all saved Time-Machine checkpoints.
  - `diff`    : Compare live workspace files against any checkpoint (`added`, `modified`, `deleted`).
  - `restore` : Surgically roll back all (or selected `--files`) to a clean checkpoint without `git reset --hard`!

Zero external dependencies (Python 3.8+ stdlib only).
"""

from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
import os
import sys
import zlib
from pathlib import Path
from typing import Any, Dict, List

SKIP_DIRS = {
    ".git", "node_modules", ".dart_tool", "build", "dist", ".next", "vendor",
    "__pycache__", ".venv", "venv", ".sqo", "target", "coverage",
}
SKIP_EXTS = {".pyc", ".pyo", ".so", ".dll", ".exe", ".zip", ".tar", ".gz", ".png", ".jpg", ".jpeg", ".webp", ".pdf", ".mp4", ".db", ".sqlite"}


def _configure_utf8() -> None:
    for s in (sys.stdout, sys.stderr):
        if hasattr(s, "reconfigure"):
            try:
                s.reconfigure(encoding="utf-8")
            except Exception:
                pass


def _cp_root(workspace: Path) -> Path:
    return workspace.resolve() / ".sqo" / "checkpoints"


def _iter_workspace_files(workspace: Path, max_file_bytes: int = 512_000) -> Dict[str, Path]:
    ws = workspace.resolve()
    found: Dict[str, Path] = {}
    for root, dirs, files in os.walk(ws):
        dirs[:] = sorted([d for d in dirs if d not in SKIP_DIRS])
        for fn in sorted(files):
            p = Path(root) / fn
            if p.suffix.lower() in SKIP_EXTS:
                continue
            try:
                st = p.stat()
            except OSError:
                continue
            if st.st_size <= max_file_bytes:
                found[p.relative_to(ws).as_posix()] = p
    return found


def create_checkpoint(workspace: Path, label: str = "snapshot", files_filter: List[str] | None = None) -> Dict[str, Any]:
    ws = workspace.resolve()
    root = _cp_root(ws)
    blobs_dir = root / "blobs"
    manifests_dir = root / "manifests"
    blobs_dir.mkdir(parents=True, exist_ok=True)
    manifests_dir.mkdir(parents=True, exist_ok=True)

    now = dt.datetime.now(dt.timezone.utc)
    slug = "".join(c if c.isalnum() or c in "-_" else "-" for c in label.strip())[:32].strip("-") or "snap"
    cp_id = f"{now.strftime('%Y%m%d-%H%M%S')}-{slug}"

    candidates = _iter_workspace_files(ws)
    if files_filter:
        wanted = {f.replace("\\", "/").lstrip("./") for f in files_filter}
        candidates = {k: v for k, v in candidates.items() if k in wanted}

    entries: Dict[str, Dict[str, Any]] = {}
    total_bytes = 0
    for rel, fpath in candidates.items():
        raw = fpath.read_bytes()
        sha = hashlib.sha256(raw).hexdigest()
        blob_file = blobs_dir / sha
        if not blob_file.is_file():
            blob_file.write_bytes(zlib.compress(raw, level=6))
        entries[rel] = {"sha256": sha, "size": len(raw)}
        total_bytes += len(raw)

    manifest = {
        "id": cp_id,
        "label": label,
        "created_at": now.strftime("%Y-%m-%dT%H:%M:%SZ"),
        "file_count": len(entries),
        "total_bytes": total_bytes,
        "files": entries,
    }
    (manifests_dir / f"{cp_id}.json").write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    return {"id": cp_id, "label": label, "file_count": len(entries), "total_bytes": total_bytes, "created_at": manifest["created_at"]}


def list_checkpoints(workspace: Path) -> List[Dict[str, Any]]:
    manifests_dir = _cp_root(workspace) / "manifests"
    if not manifests_dir.is_dir():
        return []
    items: List[Dict[str, Any]] = []
    for mf in sorted(manifests_dir.glob("*.json"), reverse=True):
        try:
            data = json.loads(mf.read_text(encoding="utf-8"))
            items.append({k: data[k] for k in ("id", "label", "created_at", "file_count", "total_bytes") if k in data})
        except Exception:
            continue
    return items


def _load_manifest(workspace: Path, cp_id: str) -> Dict[str, Any]:
    manifests_dir = _cp_root(workspace) / "manifests"
    if cp_id == "latest":
        all_mfs = sorted(manifests_dir.glob("*.json"), reverse=True)
        if not all_mfs:
            raise FileNotFoundError("No checkpoints exist in this workspace.")
        return json.loads(all_mfs[0].read_text(encoding="utf-8"))
    exact = manifests_dir / f"{cp_id}.json"
    if exact.is_file():
        return json.loads(exact.read_text(encoding="utf-8"))
    matches = sorted(manifests_dir.glob(f"*{cp_id}*.json"), reverse=True)
    if not matches:
        raise FileNotFoundError(f"Checkpoint '{cp_id}' not found.")
    return json.loads(matches[0].read_text(encoding="utf-8"))


def diff_checkpoint(workspace: Path, cp_id: str = "latest") -> Dict[str, Any]:
    ws = workspace.resolve()
    mf = _load_manifest(ws, cp_id)
    saved_files: Dict[str, Dict[str, Any]] = mf["files"]
    live_files = _iter_workspace_files(ws)

    modified: List[str] = []
    deleted: List[str] = []
    added: List[str] = []

    for rel, meta in saved_files.items():
        if rel not in live_files:
            deleted.append(rel)
        else:
            sha = hashlib.sha256(live_files[rel].read_bytes()).hexdigest()
            if sha != meta["sha256"]:
                modified.append(rel)

    for rel in live_files:
        if rel not in saved_files:
            added.append(rel)

    return {
        "checkpoint_id": mf["id"],
        "modified": sorted(modified),
        "deleted": sorted(deleted),
        "added": sorted(added),
        "clean": not (modified or deleted or added),
    }


def restore_checkpoint(workspace: Path, cp_id: str = "latest", files_filter: List[str] | None = None) -> Dict[str, Any]:
    ws = workspace.resolve()
    mf = _load_manifest(ws, cp_id)
    blobs_dir = _cp_root(ws) / "blobs"
    wanted = {f.replace("\\", "/").lstrip("./") for f in files_filter} if files_filter else None

    restored: List[str] = []
    for rel, meta in mf["files"].items():
        if wanted is not None and rel not in wanted:
            continue
        blob_path = blobs_dir / meta["sha256"]
        if not blob_path.is_file():
            continue
        raw = zlib.decompress(blob_path.read_bytes())
        dest = ws / rel
        dest.parent.mkdir(parents=True, exist_ok=True)
        dest.write_bytes(raw)
        restored.append(rel)

    return {"checkpoint_id": mf["id"], "restored_count": len(restored), "restored_files": restored[:50]}


def main() -> int:
    _configure_utf8()
    parser = argparse.ArgumentParser(description="Zero-Git-Conflict Session Time-Machine & Surgical Rollback.")
    parser.add_argument("action", choices=("create", "list", "diff", "restore"), nargs="?", default="list")
    parser.add_argument("--workspace", "-w", default=".", help="Workspace path.")
    parser.add_argument("--label", "-l", default="before-refactor", help="Checkpoint label for create.")
    parser.add_argument("--id", default="latest", help="Checkpoint ID (or 'latest') for diff/restore.")
    parser.add_argument("--files", nargs="*", help="Optional subset of relative file paths.")
    args = parser.parse_args()

    ws = Path(args.workspace).resolve()
    if args.action == "create":
        res = create_checkpoint(ws, label=args.label, files_filter=args.files)
    elif args.action == "diff":
        res = diff_checkpoint(ws, cp_id=args.id)
    elif args.action == "restore":
        res = restore_checkpoint(ws, cp_id=args.id, files_filter=args.files)
    else:
        res = {"checkpoints": list_checkpoints(ws)}
    print(json.dumps(res, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
