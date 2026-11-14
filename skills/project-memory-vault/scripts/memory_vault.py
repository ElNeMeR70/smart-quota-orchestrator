#!/usr/bin/env python3
"""Persistent Cross-Session Architectural Memory Vault (SQLite FTS5).

Eliminates the #1 hidden cross-session quota drain: every brand-new agent chat
spending 10-20 turns re-discovering where auth lives, how DB migrations run,
or why a tricky workaround exists!

Stores compact, tagged architectural facts in `<workspace>/.sqo/memory.db`
(or `$PLUGIN_DATA/memory.db`) with instant BM25 FTS5 recall in <15ms!

Subcommands:
  - remember : Store or update a project fact/decision/gotcha
  - recall   : BM25 search relevant memories for the current task
  - list     : List stored memories by category
  - forget   : Delete a memory by ID
  - stats    : Vault health & token-recovery estimate

Zero external dependencies (Python 3.8+ stdlib `sqlite3` FTS5).
"""

from __future__ import annotations

import argparse
import datetime as dt
import json
import os
import re
import sqlite3
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


def _resolve_db_path(workspace: Path, explicit_db: str = "") -> Path:
    if explicit_db:
        p = Path(explicit_db).resolve()
        p.parent.mkdir(parents=True, exist_ok=True)
        return p
    plugin_data = os.environ.get("PLUGIN_DATA")
    if plugin_data:
        base = Path(plugin_data)
        base.mkdir(parents=True, exist_ok=True)
        ws_slug = re.sub(r"[^A-Za-z0-9_.-]+", "_", workspace.name.lower()) or "default"
        return base / f"memory_{ws_slug}.db"
    sqo_dir = workspace / ".sqo"
    sqo_dir.mkdir(parents=True, exist_ok=True)
    gitignore = sqo_dir / ".gitignore"
    if not gitignore.exists():
        gitignore.write_text("*\n", encoding="utf-8")
    return sqo_dir / "memory.db"


def _init_db(db_path: Path) -> sqlite3.Connection:
    db_path.parent.mkdir(parents=True, exist_ok=True)
    con = sqlite3.connect(str(db_path))
    con.execute(
        """
        CREATE TABLE IF NOT EXISTS memories (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            category TEXT NOT NULL,
            title TEXT NOT NULL,
            detail TEXT NOT NULL,
            files TEXT NOT NULL DEFAULT '',
            created_utc TEXT NOT NULL
        )
        """
    )
    con.execute(
        """
        CREATE VIRTUAL TABLE IF NOT EXISTS memories_fts USING fts5(
            category, title, detail, files, content='memories', content_rowid='id', tokenize='unicode61'
        )
        """
    )
    return con


def remember_fact(db_path: Path, category: str, title: str, detail: str, files: List[str]) -> Dict[str, Any]:
    con = _init_db(db_path)
    now = dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    files_str = ", ".join(files)
    cur = con.execute(
        "INSERT INTO memories(category, title, detail, files, created_utc) VALUES (?, ?, ?, ?, ?)",
        (category.strip().lower(), title.strip(), detail.strip(), files_str, now),
    )
    rowid = int(cur.lastrowid or 0)
    con.execute(
        "INSERT INTO memories_fts(rowid, category, title, detail, files) VALUES (?, ?, ?, ?, ?)",
        (rowid, category.strip().lower(), title.strip(), detail.strip(), files_str),
    )
    con.commit()
    con.close()
    return {"id": rowid, "category": category, "title": title, "detail": detail, "files": files, "created_utc": now}


def recall_facts(db_path: Path, query: str, limit: int = 8) -> List[Dict[str, Any]]:
    if not db_path.is_file():
        return []
    con = _init_db(db_path)
    tokens = [f'"{t}"' for t in re.findall(r"[A-Za-z0-9_]{2,}", query)[:10]]
    if not tokens:
        cur = con.execute("SELECT id, category, title, detail, files, created_utc FROM memories ORDER BY id DESC LIMIT ?", (limit,))
    else:
        fts_q = " OR ".join(tokens)
        cur = con.execute(
            """
            SELECT m.id, m.category, m.title, m.detail, m.files, m.created_utc
            FROM memories_fts f
            JOIN memories m ON m.id = f.rowid
            WHERE memories_fts MATCH ?
            ORDER BY bm25(memories_fts, 1.5, 4.0, 2.0, 2.5) ASC
            LIMIT ?
            """,
            (fts_q, limit),
        )
    rows = [
        {"id": r[0], "category": r[1], "title": r[2], "detail": r[3], "files": r[4], "created_utc": r[5]}
        for r in cur.fetchall()
    ]
    con.close()
    return rows


def list_facts(db_path: Path, category: str = "", limit: int = 20) -> List[Dict[str, Any]]:
    if not db_path.is_file():
        return []
    con = _init_db(db_path)
    if category:
        cur = con.execute(
            "SELECT id, category, title, detail, files, created_utc FROM memories WHERE category = ? ORDER BY id DESC LIMIT ?",
            (category.lower(), limit),
        )
    else:
        cur = con.execute("SELECT id, category, title, detail, files, created_utc FROM memories ORDER BY id DESC LIMIT ?", (limit,))
    rows = [
        {"id": r[0], "category": r[1], "title": r[2], "detail": r[3], "files": r[4], "created_utc": r[5]}
        for r in cur.fetchall()
    ]
    con.close()
    return rows


def forget_fact(db_path: Path, mem_id: int) -> bool:
    if not db_path.is_file():
        return False
    con = _init_db(db_path)
    row = con.execute("SELECT id, category, title, detail, files FROM memories WHERE id = ?", (mem_id,)).fetchone()
    if not row:
        con.close()
        return False
    con.execute(
        "INSERT INTO memories_fts(memories_fts, rowid, category, title, detail, files) VALUES('delete', ?, ?, ?, ?, ?)",
        row,
    )
    con.execute("DELETE FROM memories WHERE id = ?", (mem_id,))
    con.commit()
    con.close()
    return True


def render_memories_md(items: List[Dict[str, Any]], heading: str) -> str:
    lines = [f"## {heading} (`{len(items)}` item(s))", ""]
    if not items:
        lines.append("_No stored architectural memories matched._")
        return "\n".join(lines)
    for m in items:
        files_part = f" — Files: `{m['files']}`" if m.get("files") else ""
        lines.append(f"- **`#{m['id']}` [{m['category']}] {m['title']}**: {m['detail']}{files_part}")
    return "\n".join(lines)


def main() -> int:
    _configure_utf8()
    parser = argparse.ArgumentParser(description="Persistent cross-session SQLite FTS5 architectural memory vault.")
    parser.add_argument("--workspace", "-w", default=".", help="Workspace root.")
    parser.add_argument("--db", default="", help="Optional explicit SQLite DB file path.")
    parser.add_argument("--format", choices=("markdown", "json"), default="markdown", help="Output format.")

    sub = parser.add_subparsers(dest="action", required=True)

    p_rem = sub.add_parser("remember", help="Store an architectural decision, convention, or gotcha.")
    p_rem.add_argument("--category", "-c", default="architecture", help="Category (architecture, auth, db, build, gotcha).")
    p_rem.add_argument("--title", "-t", required=True, help="Short headline.")
    p_rem.add_argument("--detail", "-d", required=True, help="Concise factual explanation.")
    p_rem.add_argument("--files", "-f", nargs="*", default=[], help="Associated relative file paths.")

    p_rec = sub.add_parser("recall", help="Query relevant memories via BM25.")
    p_rec.add_argument("query", help="Search keywords or task summary.")
    p_rec.add_argument("--limit", "-k", type=int, default=8)

    p_lst = sub.add_parser("list", help="List recent memories.")
    p_lst.add_argument("--category", "-c", default="")
    p_lst.add_argument("--limit", "-k", type=int, default=20)

    p_del = sub.add_parser("forget", help="Remove a stored memory by numeric ID.")
    p_del.add_argument("id", type=int)

    args = parser.parse_args()
    db_path = _resolve_db_path(Path(args.workspace).resolve(), args.db)

    if args.action == "remember":
        saved = remember_fact(db_path, args.category, args.title, args.detail, args.files)
        print(json.dumps(saved, indent=2, ensure_ascii=False) if args.format == "json" else f"[OK] Stored Memory `#{saved['id']}`: **{saved['title']}**")
    elif args.action == "recall":
        items = recall_facts(db_path, args.query, limit=args.limit)
        print(json.dumps(items, indent=2, ensure_ascii=False) if args.format == "json" else render_memories_md(items, f"Recalled Memories for '{args.query}'"))
    elif args.action == "list":
        items = list_facts(db_path, category=args.category, limit=args.limit)
        print(json.dumps(items, indent=2, ensure_ascii=False) if args.format == "json" else render_memories_md(items, "Project Memory Vault"))
    elif args.action == "forget":
        ok = forget_fact(db_path, args.id)
        print(json.dumps({"deleted": ok, "id": args.id}) if args.format == "json" else (f"[OK] Deleted memory #{args.id}" if ok else f"[WARN] Memory #{args.id} not found"))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
