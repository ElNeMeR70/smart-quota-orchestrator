#!/usr/bin/env python3
"""Claude-Mem + Graphiti Zero-Effort Auto-Captured Temporal Knowledge Graph (v10.0 Apex).

Automatically observes file edits, command failures, and bugfix resolutions via
PostToolUse hooks (<4ms) and builds a relational Entity-Edge Knowledge Graph in
`.sqo/memory_graph.db` with Mermaid diagram export and per-file history recall!
"""

from __future__ import annotations

import argparse
import json
import sqlite3
import time
from pathlib import Path
from typing import Any, Dict, List


def _db_path(workspace: Path) -> Path:
    d = workspace.resolve() / ".sqo"
    d.mkdir(parents=True, exist_ok=True)
    return d / "memory_graph.db"


def _connect(workspace: Path) -> sqlite3.Connection:
    conn = sqlite3.connect(str(_db_path(workspace)), timeout=1.5)
    conn.row_factory = sqlite3.Row
    conn.executescript(
        """
        CREATE TABLE IF NOT EXISTS kg_nodes (
            node_id TEXT PRIMARY KEY,
            kind TEXT NOT NULL,
            label TEXT NOT NULL,
            summary TEXT NOT NULL DEFAULT '',
            touch_count INTEGER NOT NULL DEFAULT 1,
            updated_at REAL NOT NULL
        );
        CREATE TABLE IF NOT EXISTS kg_edges (
            src_id TEXT NOT NULL,
            rel TEXT NOT NULL,
            dst_id TEXT NOT NULL,
            note TEXT NOT NULL DEFAULT '',
            weight INTEGER NOT NULL DEFAULT 1,
            updated_at REAL NOT NULL,
            PRIMARY KEY (src_id, rel, dst_id)
        );
        """
    )
    return conn


def upsert_node(conn: sqlite3.Connection, node_id: str, kind: str, label: str, summary: str = "") -> None:
    now = time.time()
    conn.execute(
        """
        INSERT INTO kg_nodes(node_id, kind, label, summary, touch_count, updated_at)
        VALUES (?, ?, ?, ?, 1, ?)
        ON CONFLICT(node_id) DO UPDATE SET
            summary = CASE WHEN excluded.summary != '' THEN excluded.summary ELSE kg_nodes.summary END,
            touch_count = kg_nodes.touch_count + 1,
            updated_at = excluded.updated_at
        """,
        (node_id, kind, label, summary[:280], now),
    )


def upsert_edge(conn: sqlite3.Connection, src_id: str, rel: str, dst_id: str, note: str = "") -> None:
    now = time.time()
    conn.execute(
        """
        INSERT INTO kg_edges(src_id, rel, dst_id, note, weight, updated_at)
        VALUES (?, ?, ?, ?, 1, ?)
        ON CONFLICT(src_id, rel, dst_id) DO UPDATE SET
            note = CASE WHEN excluded.note != '' THEN excluded.note ELSE kg_edges.note END,
            weight = kg_edges.weight + 1,
            updated_at = excluded.updated_at
        """,
        (src_id, rel, dst_id, note[:240], now),
    )


def record_auto_observation(
    workspace: Path,
    event_kind: str,
    file_rel: str = "",
    command: str = "",
    note: str = "",
    co_edited_file: str = "",
) -> Dict[str, Any]:
    """Ultra-fast (<4ms) auto-capture entrypoint invoked silently by PostToolUse hook."""
    conn = _connect(workspace)
    try:
        if file_rel:
            fid = f"file:{file_rel}"
            upsert_node(conn, fid, "file", file_rel, note)
            if co_edited_file and co_edited_file != file_rel:
                cid = f"file:{co_edited_file}"
                upsert_node(conn, cid, "file", co_edited_file, "")
                upsert_edge(conn, fid, "CO_EDITED_WITH", cid, "Modified in same session flow")

        if event_kind == "bugfix_resolved" and file_rel and command:
            fid = f"file:{file_rel}"
            bid = f"bugfix:{command[:60]}"
            upsert_node(conn, fid, "file", file_rel, note)
            upsert_node(conn, bid, "bugfix", command[:60], note or "Failed command resolved after editing file")
            upsert_edge(conn, fid, "RESOLVED_FAILURE", bid, note or "Edit fixed failing command")
        elif event_kind == "rule" and file_rel and note:
            fid = f"file:{file_rel}"
            rid = f"rule:{note[:48]}"
            upsert_node(conn, fid, "file", file_rel, "")
            upsert_node(conn, rid, "rule", note[:64], note)
            upsert_edge(conn, fid, "GOVERNED_BY", rid, note)

        conn.commit()
        return {"ok": True, "event_kind": event_kind, "file": file_rel}
    finally:
        conn.close()


def query_file_history(workspace: Path, file_rel: str) -> Dict[str, Any]:
    file_rel = file_rel.replace("\\", "/")
    fid = f"file:{file_rel}"
    conn = _connect(workspace)
    try:
        node = conn.execute("SELECT * FROM kg_nodes WHERE node_id = ?", (fid,)).fetchone()
        edges = conn.execute(
            """
            SELECT e.src_id, e.rel, e.dst_id, e.note, e.weight, n.label AS other_label, n.kind AS other_kind
            FROM kg_edges e
            LEFT JOIN kg_nodes n ON (CASE WHEN e.src_id = ? THEN e.dst_id ELSE e.src_id END) = n.node_id
            WHERE e.src_id = ? OR e.dst_id = ?
            ORDER BY e.weight DESC, e.updated_at DESC LIMIT 15
            """,
            (fid, fid, fid),
        ).fetchall()
        return {
            "file": file_rel,
            "touch_count": int(node["touch_count"]) if node else 0,
            "summary": str(node["summary"]) if node else "",
            "relations": [dict(r) for r in edges],
        }
    finally:
        conn.close()


def graph_summary(workspace: Path, limit: int = 20) -> Dict[str, Any]:
    conn = _connect(workspace)
    try:
        nodes = [dict(r) for r in conn.execute("SELECT * FROM kg_nodes ORDER BY touch_count DESC, updated_at DESC LIMIT ?", (limit,)).fetchall()]
        edges = [dict(r) for r in conn.execute("SELECT * FROM kg_edges ORDER BY weight DESC, updated_at DESC LIMIT ?", (limit,)).fetchall()]
        mermaid = ["flowchart LR"]
        for idx, e in enumerate(edges[:12], 1):
            s = e["src_id"].replace(":", "_").replace("/", "_").replace(".", "_").replace(" ", "_")[:28]
            d = e["dst_id"].replace(":", "_").replace("/", "_").replace(".", "_").replace(" ", "_")[:28]
            sl = e["src_id"].split(":", 1)[-1]
            dl = e["dst_id"].split(":", 1)[-1]
            mermaid.append(f'  {s}_{idx}["{sl}"] -->|"{e["rel"]} (x{e["weight"]})"| {d}_{idx}["{dl}"]')
        return {
            "node_count": len(nodes),
            "edge_count": len(edges),
            "top_nodes": nodes,
            "top_edges": edges,
            "mermaid": "\n".join(mermaid),
        }
    finally:
        conn.close()


def render_markdown(res: Dict[str, Any]) -> str:
    if "relations" in res:
        lines = [f"### 🧠 Temporal Memory Graph for `{res['file']}` (Touches: {res['touch_count']})"]
        if res.get("summary"):
            lines.append(f"- **Latest Note:** {res['summary']}")
        for r in res["relations"]:
            lines.append(f"- `{r['rel']}` -> **{r.get('other_label') or r['dst_id']}** (×{r['weight']}): {r['note']}")
        if not res["relations"]:
            lines.append("- _No recorded graph edges yet._")
        return "\n".join(lines)

    lines = [
        f"### 🧠 Auto-Captured Knowledge Graph ({res.get('node_count', 0)} nodes • {res.get('edge_count', 0)} edges)",
        "```mermaid",
        res.get("mermaid", "flowchart LR"),
        "```",
    ]
    return "\n".join(lines)


def main() -> int:
    ap = argparse.ArgumentParser(description="Auto-Captured Temporal Knowledge Graph")
    ap.add_argument("action", choices=["summary", "file", "record"], nargs="?", default="summary")
    ap.add_argument("--workspace", default=".")
    ap.add_argument("--file", default="")
    ap.add_argument("--event", default="edit")
    ap.add_argument("--command", default="")
    ap.add_argument("--note", default="")
    ap.add_argument("--json", action="store_true")
    ns = ap.parse_args()

    ws = Path(ns.workspace).resolve()
    if ns.action == "file":
        out = query_file_history(ws, ns.file)
    elif ns.action == "record":
        out = record_auto_observation(ws, ns.event, file_rel=ns.file, command=ns.command, note=ns.note)
    else:
        out = graph_summary(ws)

    print(json.dumps(out, indent=2, ensure_ascii=False) if ns.json else render_markdown(out))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
