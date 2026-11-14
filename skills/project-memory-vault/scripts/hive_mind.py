#!/usr/bin/env python3
"""Cross-Project Federated Hive-Mind Brain (`sqo hive` / `sqo_hive_mind`).

Unifies architectural wisdom, bug root-causes, and framework gotchas across ALL repositories
on a developer's machine into `~/.sqo/hive_mind.db` (SQLite FTS5 BM25 + automatic secret scrubbing):
  - `promote` : Promote reusable memories from a project's `.sqo/memory.db` (or add directly) into Global Hive-Mind.
  - `recall`  : Query universal + stack-specific lessons (`flutter`, `nextjs`, `laravel`, `python`, etc.) in <10ms.
  - `inject`  : Seed matching Global Hive-Mind lessons into a brand-new workspace's `.sqo/memory.db` on Turn 0!
  - `stats`   : Inspect federated stacks, total wisdom entries, and top recalled patterns.

Zero external dependencies (Python 3.8+ stdlib only).
"""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import sqlite3
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional


def _configure_utf8() -> None:
    for stream in (sys.stdout, sys.stderr):
        if hasattr(stream, "reconfigure"):
            try:
                stream.reconfigure(encoding="utf-8")
            except Exception:
                pass


def default_hive_path(override: Optional[str | Path] = None) -> Path:
    if override:
        return Path(override).resolve()
    return Path.home() / ".sqo" / "hive_mind.db"


def _scrub(text: str) -> str:
    scrub_file = Path(__file__).resolve().parent / "scrub_secrets.py"
    if scrub_file.is_file():
        spec = importlib.util.spec_from_file_location("scrub_secrets", scrub_file)
        if spec and spec.loader:
            mod = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(mod)
            return str(mod.scrub_text(text)["scrubbed_text"])
    return text


def detect_stack(workspace: Path) -> str:
    if (workspace / "pubspec.yaml").is_file():
        return "flutter"
    if (workspace / "artisan").is_file() or (workspace / "composer.json").is_file():
        return "laravel"
    if (workspace / "next.config.js").is_file() or (workspace / "next.config.mjs").is_file() or (workspace / "next.config.ts").is_file():
        return "nextjs"
    if (workspace / "package.json").is_file():
        return "nodejs"
    if (workspace / "Cargo.toml").is_file():
        return "rust"
    if (workspace / "go.mod").is_file():
        return "go"
    if (workspace / "pyproject.toml").is_file() or (workspace / "requirements.txt").is_file():
        return "python"
    return "universal"


def _connect(hive_db: Path) -> sqlite3.Connection:
    hive_db.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(str(hive_db))
    conn.row_factory = sqlite3.Row
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS hive_lessons (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            fingerprint TEXT UNIQUE NOT NULL,
            stack TEXT NOT NULL,
            category TEXT NOT NULL,
            title TEXT NOT NULL,
            detail TEXT NOT NULL,
            source_repo TEXT NOT NULL,
            reuse_count INTEGER NOT NULL DEFAULT 1,
            created_at TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%SZ', 'now'))
        )
        """
    )
    try:
        conn.execute(
            """
            CREATE VIRTUAL TABLE IF NOT EXISTS hive_fts USING fts5(
                stack, category, title, detail, content='hive_lessons', content_rowid='id'
            )
            """
        )
    except sqlite3.OperationalError:
        pass
    return conn


def _rebuild_fts(conn: sqlite3.Connection) -> None:
    try:
        conn.execute("INSERT INTO hive_fts(hive_fts) VALUES('rebuild')")
    except sqlite3.OperationalError:
        pass


def store_hive_lesson(
    hive_db: Path,
    stack: str,
    category: str,
    title: str,
    detail: str,
    source_repo: str = "global",
) -> Dict[str, Any]:
    clean_title = _scrub(title.strip())
    clean_detail = _scrub(detail.strip())
    norm_stack = (stack or "universal").strip().lower()
    norm_cat = (category or "architecture").strip().lower()
    fp = hashlib.sha256(f"{norm_stack}|{clean_title.lower()}|{clean_detail.lower()}".encode("utf-8")).hexdigest()[:24]

    conn = _connect(hive_db)
    try:
        cur = conn.execute("SELECT id, reuse_count FROM hive_lessons WHERE fingerprint = ?", (fp,)).fetchone()
        if cur:
            new_count = int(cur["reuse_count"]) + 1
            conn.execute("UPDATE hive_lessons SET reuse_count = ? WHERE id = ?", (new_count, int(cur["id"])))
            conn.commit()
            return {"id": int(cur["id"]), "stack": norm_stack, "title": clean_title, "deduplicated": True, "reuse_count": new_count}

        ins = conn.execute(
            """
            INSERT INTO hive_lessons (fingerprint, stack, category, title, detail, source_repo)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (fp, norm_stack, norm_cat, clean_title, clean_detail, source_repo),
        )
        lesson_id = int(ins.lastrowid or 0)
        _rebuild_fts(conn)
        conn.commit()
        return {"id": lesson_id, "stack": norm_stack, "title": clean_title, "deduplicated": False, "reuse_count": 1}
    finally:
        conn.close()


def promote_from_workspace(workspace: Path, hive_db: Path, stack: str = "auto") -> Dict[str, Any]:
    ws = workspace.resolve()
    resolved_stack = detect_stack(ws) if stack == "auto" else stack.lower()
    mem_script = Path(__file__).resolve().parent / "memory_vault.py"
    spec = importlib.util.spec_from_file_location("memory_vault", mem_script)
    assert spec and spec.loader
    mem_mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mem_mod)

    local_db = mem_mod._resolve_db_path(ws)
    facts = mem_mod.list_facts(local_db, limit=100)
    promoted = 0
    deduped = 0
    for f in facts:
        res = store_hive_lesson(
            hive_db,
            stack=resolved_stack,
            category=str(f.get("category", "architecture")),
            title=str(f.get("title", "")),
            detail=str(f.get("detail", "")),
            source_repo=ws.name,
        )
        if res["deduplicated"]:
            deduped += 1
        else:
            promoted += 1
    return {
        "workspace": ws.name,
        "stack": resolved_stack,
        "scanned_local_facts": len(facts),
        "newly_promoted": promoted,
        "deduplicated_existing": deduped,
    }


def recall_hive(hive_db: Path, query: str = "", stack: str = "", limit: int = 8) -> List[Dict[str, Any]]:
    if not hive_db.is_file():
        return []
    conn = _connect(hive_db)
    try:
        tokens = [t for t in "".join(ch if ch.isalnum() else " " for ch in query).split() if len(t) >= 2]
        rows: List[sqlite3.Row] = []
        if tokens:
            fts_q = " OR ".join(f'"{t}"*' for t in tokens[:8])
            try:
                if stack and stack != "all":
                    rows = conn.execute(
                        """
                        SELECT l.* FROM hive_fts f
                        JOIN hive_lessons l ON l.id = f.rowid
                        WHERE hive_fts MATCH ? AND l.stack IN (?, 'universal')
                        ORDER BY bm25(hive_fts), l.reuse_count DESC LIMIT ?
                        """,
                        (fts_q, stack.lower(), limit),
                    ).fetchall()
                else:
                    rows = conn.execute(
                        """
                        SELECT l.* FROM hive_fts f
                        JOIN hive_lessons l ON l.id = f.rowid
                        WHERE hive_fts MATCH ?
                        ORDER BY bm25(hive_fts), l.reuse_count DESC LIMIT ?
                        """,
                        (fts_q, limit),
                    ).fetchall()
            except sqlite3.OperationalError:
                rows = []

        if not rows:
            if stack and stack != "all":
                rows = conn.execute(
                    "SELECT * FROM hive_lessons WHERE stack IN (?, 'universal') ORDER BY reuse_count DESC, id DESC LIMIT ?",
                    (stack.lower(), limit),
                ).fetchall()
            else:
                rows = conn.execute(
                    "SELECT * FROM hive_lessons ORDER BY reuse_count DESC, id DESC LIMIT ?",
                    (limit,),
                ).fetchall()
        return [dict(r) for r in rows]
    finally:
        conn.close()


def inject_into_workspace(workspace: Path, hive_db: Path, stack: str = "auto", limit: int = 6) -> Dict[str, Any]:
    ws = workspace.resolve()
    resolved_stack = detect_stack(ws) if stack == "auto" else stack.lower()
    lessons = recall_hive(hive_db, query="", stack=resolved_stack, limit=limit)

    mem_script = Path(__file__).resolve().parent / "memory_vault.py"
    spec = importlib.util.spec_from_file_location("memory_vault", mem_script)
    assert spec and spec.loader
    mem_mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mem_mod)

    local_db = mem_mod._resolve_db_path(ws)
    injected = 0
    for item in lessons:
        mem_mod.remember_fact(
            local_db,
            category=f"hive:{item['stack']}",
            title=str(item["title"]),
            detail=str(item["detail"]),
            files=[],
        )
        injected += 1
    return {"workspace": ws.name, "stack": resolved_stack, "injected_count": injected}


def hive_stats(hive_db: Path) -> Dict[str, Any]:
    if not hive_db.is_file():
        return {"total_lessons": 0, "stacks": {}, "repos_federated": 0}
    conn = _connect(hive_db)
    try:
        total = int(conn.execute("SELECT COUNT(*) FROM hive_lessons").fetchone()[0])
        repos = int(conn.execute("SELECT COUNT(DISTINCT source_repo) FROM hive_lessons").fetchone()[0])
        by_stack = {
            str(r["stack"]): int(r["c"])
            for r in conn.execute("SELECT stack, COUNT(*) AS c FROM hive_lessons GROUP BY stack ORDER BY c DESC").fetchall()
        }
        return {"total_lessons": total, "repos_federated": repos, "stacks": by_stack, "hive_db": str(hive_db)}
    finally:
        conn.close()


def render_markdown(items: List[Dict[str, Any]], stats: Dict[str, Any]) -> str:
    lines = [
        f"## 🧬 Cross-Project Hive-Mind Brain (`{stats.get('total_lessons', 0)}` Federated Lessons across `{stats.get('repos_federated', 0)}` Repos)",
        "",
    ]
    if not items:
        lines.append("_No Hive-Mind lessons stored yet. Run `python sqo.py hive promote --workspace .` to federate your project wisdom!_")
        return "\n".join(lines)
    for it in items:
        lines.append(f"- **[`{it['stack']}` | `{it['category']}`] {it['title']}** _(from `{it['source_repo']}`, reused ×{it['reuse_count']})_: {it['detail']}")
    return "\n".join(lines)


def main() -> int:
    _configure_utf8()
    parser = argparse.ArgumentParser(description="Cross-Project Federated Hive-Mind Brain.")
    parser.add_argument("action", choices=("promote", "recall", "inject", "stats"), nargs="?", default="stats")
    parser.add_argument("--workspace", "-w", default=".", help="Workspace path.")
    parser.add_argument("--stack", default="auto", help="Tech stack filter (flutter, nextjs, laravel, python, universal, auto).")
    parser.add_argument("--query", "-q", default="", help="BM25 search query for recall.")
    parser.add_argument("--title", default="", help="Direct lesson title to store during promote.")
    parser.add_argument("--detail", default="", help="Direct lesson detail to store during promote.")
    parser.add_argument("--category", default="gotcha", help="Lesson category.")
    parser.add_argument("--hive-db", default="", help="Optional custom Hive DB path.")
    parser.add_argument("--format", choices=("markdown", "json"), default="markdown")
    args = parser.parse_args()

    hive_db = default_hive_path(args.hive_db or None)
    ws = Path(args.workspace).resolve()

    if args.action == "promote":
        if args.title and args.detail:
            st = detect_stack(ws) if args.stack == "auto" else args.stack
            res = store_hive_lesson(hive_db, st, args.category, args.title, args.detail, source_repo=ws.name)
        else:
            res = promote_from_workspace(ws, hive_db, stack=args.stack)
        print(json.dumps(res, indent=2, ensure_ascii=False))
        return 0

    if args.action == "inject":
        res = inject_into_workspace(ws, hive_db, stack=args.stack)
        print(json.dumps(res, indent=2, ensure_ascii=False))
        return 0

    st_filter = "" if args.stack in ("auto", "all") else args.stack
    items = recall_hive(hive_db, query=args.query, stack=st_filter, limit=10)
    st_info = hive_stats(hive_db)
    if args.format == "json":
        print(json.dumps({"stats": st_info, "lessons": items}, indent=2, ensure_ascii=False))
    else:
        print(render_markdown(items, st_info))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
