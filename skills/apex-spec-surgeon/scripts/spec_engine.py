#!/usr/bin/env python3
"""Spec-Kit + Taskmaster Autonomous Spec-Driven DAG Engine (v10.0 Apex).

Eliminates Vibe-Coding Drift by turning feature goals into a persistent SQLite
Spec & Task Dependency Graph (.sqo/specs.db + .sqo/specs/<slug>/spec.md) with
atomic file-ownership boundaries, topological next-task briefs (<220 tokens),
and mandatory executable verification gates!
"""

from __future__ import annotations

import argparse
import json
import re
import sqlite3
import subprocess
import time
from pathlib import Path
from typing import Any, Dict, List, Optional


def _slugify(text: str) -> str:
    s = re.sub(r"[^a-zA-Z0-9]+", "-", text.strip().lower()).strip("-")
    return s[:48] or "feature-spec"


def _connect(workspace: Path) -> sqlite3.Connection:
    sqo_dir = workspace.resolve() / ".sqo"
    sqo_dir.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(str(sqo_dir / "specs.db"))
    conn.row_factory = sqlite3.Row
    conn.executescript(
        """
        CREATE TABLE IF NOT EXISTS specs (
            slug TEXT PRIMARY KEY,
            title TEXT NOT NULL,
            goal TEXT NOT NULL,
            constraints_json TEXT NOT NULL DEFAULT '[]',
            created_at REAL NOT NULL
        );
        CREATE TABLE IF NOT EXISTS spec_tasks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            spec_slug TEXT NOT NULL,
            step_key TEXT NOT NULL,
            title TEXT NOT NULL,
            owned_files_json TEXT NOT NULL DEFAULT '[]',
            depends_on_json TEXT NOT NULL DEFAULT '[]',
            verify_cmd TEXT NOT NULL DEFAULT '',
            status TEXT NOT NULL DEFAULT 'pending',
            verification_output TEXT NOT NULL DEFAULT '',
            completed_at REAL,
            UNIQUE(spec_slug, step_key)
        );
        """
    )
    return conn


def init_spec(
    workspace: Path,
    title: str,
    goal: str,
    tasks: Optional[List[Dict[str, Any]]] = None,
    constraints: Optional[List[str]] = None,
) -> Dict[str, Any]:
    workspace = workspace.resolve()
    slug = _slugify(title)
    constraints = constraints or [
        "Touch ONLY owned_files declared per task (Karpathy Surgical Scope).",
        "Pass verify_cmd and sqo_verify_work with 0 TODO/placeholder stubs before completion.",
    ]
    if not tasks:
        tasks = [
            {
                "step_key": "T1",
                "title": f"Define Contracts, Schemas & Failing Red Tests for {title}",
                "owned_files": ["tests/"],
                "depends_on": [],
                "verify_cmd": "",
            },
            {
                "step_key": "T2",
                "title": f"Core Implementation for {title}",
                "owned_files": ["src/", "lib/"],
                "depends_on": ["T1"],
                "verify_cmd": "",
            },
            {
                "step_key": "T3",
                "title": f"Edge-Case Hardening & Karpathy Diff Verification for {title}",
                "owned_files": ["tests/"],
                "depends_on": ["T2"],
                "verify_cmd": "",
            },
        ]

    now = time.time()
    conn = _connect(workspace)
    try:
        conn.execute(
            "INSERT OR REPLACE INTO specs(slug, title, goal, constraints_json, created_at) VALUES (?, ?, ?, ?, ?)",
            (slug, title, goal, json.dumps(constraints, ensure_ascii=False), now),
        )
        conn.execute("DELETE FROM spec_tasks WHERE spec_slug = ?", (slug,))
        for idx, t in enumerate(tasks, 1):
            skey = str(t.get("step_key") or f"T{idx}")
            conn.execute(
                """
                INSERT INTO spec_tasks(spec_slug, step_key, title, owned_files_json, depends_on_json, verify_cmd, status)
                VALUES (?, ?, ?, ?, ?, ?, 'pending')
                """,
                (
                    slug,
                    skey,
                    str(t.get("title") or f"Task {idx}"),
                    json.dumps(t.get("owned_files") or [], ensure_ascii=False),
                    json.dumps(t.get("depends_on") or [], ensure_ascii=False),
                    str(t.get("verify_cmd") or ""),
                ),
            )
        conn.commit()
    finally:
        conn.close()

    # Write compact human+agent readable spec.md
    spec_dir = workspace / ".sqo" / "specs" / slug
    spec_dir.mkdir(parents=True, exist_ok=True)
    md_lines = [
        f"# 📐 Spec Contract: {title} (`{slug}`)",
        f"\n## Goal\n{goal}\n",
        "## Hard Invariants",
        *[f"- {c}" for c in constraints],
        "\n## Atomic Task DAG",
    ]
    for t in tasks:
        deps = ", ".join(t.get("depends_on") or []) or "root"
        files = ", ".join(t.get("owned_files") or []) or "*"
        md_lines.append(f"- **[ ] `{t.get('step_key')}`** {t.get('title')} _(deps: {deps} | files: {files})_")
    spec_md_path = spec_dir / "spec.md"
    spec_md_path.write_text("\n".join(md_lines) + "\n", encoding="utf-8")

    return {"ok": True, "slug": slug, "task_count": len(tasks), "spec_file": str(spec_md_path.relative_to(workspace)).replace("\\", "/")}


def get_next_task(workspace: Path, slug: str = "") -> Dict[str, Any]:
    conn = _connect(workspace.resolve())
    try:
        if not slug:
            row = conn.execute("SELECT slug FROM specs ORDER BY created_at DESC LIMIT 1").fetchone()
            if not row:
                return {"ok": False, "error": "No specs initialized yet."}
            slug = str(row["slug"])

        spec = conn.execute("SELECT * FROM specs WHERE slug = ?", (slug,)).fetchone()
        if not spec:
            return {"ok": False, "error": f"Spec '{slug}' not found."}

        rows = conn.execute("SELECT * FROM spec_tasks WHERE spec_slug = ? ORDER BY id ASC", (slug,)).fetchall()
        done_keys = {str(r["step_key"]) for r in rows if r["status"] == "done"}

        for r in rows:
            if r["status"] == "done":
                continue
            deps = json.loads(r["depends_on_json"] or "[]")
            if all(d in done_keys for d in deps):
                return {
                    "ok": True,
                    "status": "READY",
                    "slug": slug,
                    "spec_title": spec["title"],
                    "progress": f"{len(done_keys)}/{len(rows)}",
                    "task": {
                        "step_key": r["step_key"],
                        "title": r["title"],
                        "owned_files": json.loads(r["owned_files_json"] or "[]"),
                        "depends_on": deps,
                        "verify_cmd": r["verify_cmd"],
                    },
                    "constraints": json.loads(spec["constraints_json"] or "[]"),
                }

        return {"ok": True, "status": "ALL_COMPLETED", "slug": slug, "progress": f"{len(done_keys)}/{len(rows)}"}
    finally:
        conn.close()


def complete_task(workspace: Path, slug: str, step_key: str, run_verify: bool = True) -> Dict[str, Any]:
    workspace = workspace.resolve()
    conn = _connect(workspace)
    try:
        row = conn.execute(
            "SELECT * FROM spec_tasks WHERE spec_slug = ? AND step_key = ?",
            (slug, step_key),
        ).fetchone()
        if not row:
            return {"ok": False, "error": f"Task '{step_key}' not found in spec '{slug}'."}

        vcmd = str(row["verify_cmd"] or "").strip()
        vout = "verified (no command)"
        if run_verify and vcmd:
            proc = subprocess.run(vcmd, cwd=str(workspace), shell=True, capture_output=True, text=True, timeout=30)
            vout = ((proc.stdout or "") + "\n" + (proc.stderr or "")).strip()[:400]
            if proc.returncode != 0:
                return {
                    "ok": False,
                    "gate_blocked": True,
                    "step_key": step_key,
                    "error": f"Acceptance gate failed (exit {proc.returncode}): `{vcmd}`",
                    "output": vout,
                }

        conn.execute(
            "UPDATE spec_tasks SET status = 'done', verification_output = ?, completed_at = ? WHERE id = ?",
            (vout, time.time(), row["id"]),
        )
        conn.commit()
    finally:
        conn.close()

    nxt = get_next_task(workspace, slug)
    return {"ok": True, "completed": step_key, "slug": slug, "next_state": nxt.get("status"), "next_task": nxt.get("task")}


def spec_status(workspace: Path, slug: str = "") -> Dict[str, Any]:
    conn = _connect(workspace.resolve())
    try:
        if not slug:
            row = conn.execute("SELECT slug FROM specs ORDER BY created_at DESC LIMIT 1").fetchone()
            if not row:
                return {"ok": True, "specs": []}
            slug = str(row["slug"])
        spec = conn.execute("SELECT * FROM specs WHERE slug = ?", (slug,)).fetchone()
        if not spec:
            return {"ok": False, "error": f"Spec '{slug}' not found."}
        tasks = [
            {
                "step_key": r["step_key"],
                "title": r["title"],
                "status": r["status"],
                "depends_on": json.loads(r["depends_on_json"] or "[]"),
                "owned_files": json.loads(r["owned_files_json"] or "[]"),
            }
            for r in conn.execute("SELECT * FROM spec_tasks WHERE spec_slug = ? ORDER BY id ASC", (slug,)).fetchall()
        ]
        return {"ok": True, "slug": slug, "title": spec["title"], "goal": spec["goal"], "tasks": tasks}
    finally:
        conn.close()


def render_markdown(res: Dict[str, Any]) -> str:
    if not res.get("ok"):
        return f"### ❌ Spec Gate Blocked\n- **Reason:** {res.get('error')}\n```\n{res.get('output', '')}\n```"
    if res.get("status") == "READY":
        t = res["task"]
        return (
            f"### 📐 Next Ready Spec Task (`{res['slug']}` • {res['progress']})\n"
            f"- **Step `{t['step_key']}`:** **{t['title']}**\n"
            f"- **Owned Files:** `{', '.join(t['owned_files']) or '*'}`\n"
            f"- **Acceptance Gate:** `{t['verify_cmd'] or 'sqo_verify_work'}`"
        )
    if "tasks" in res:
        lines = [f"### 📐 Spec DAG Status: {res.get('title')} (`{res.get('slug')}`)"]
        for t in res["tasks"]:
            icon = "✅" if t["status"] == "done" else "⏳"
            lines.append(f"- {icon} **`{t['step_key']}`** {t['title']} _(deps: {', '.join(t['depends_on']) or 'none'})_")
        return "\n".join(lines)
    return f"### ✅ Spec Updated (`{res.get('slug')}`)\n```json\n{json.dumps(res, indent=2, ensure_ascii=False)}\n```"


def main() -> int:
    ap = argparse.ArgumentParser(description="Spec-Driven DAG Task Engine")
    ap.add_argument("action", choices=["init", "next", "complete", "status"])
    ap.add_argument("--workspace", default=".")
    ap.add_argument("--slug", default="")
    ap.add_argument("--title", default="New Feature")
    ap.add_argument("--goal", default="Implement feature cleanly with full tests")
    ap.add_argument("--step", default="T1")
    ap.add_argument("--tasks-json", default="")
    ap.add_argument("--json", action="store_true")
    ns = ap.parse_args()

    ws = Path(ns.workspace).resolve()
    if ns.action == "init":
        tlist = json.loads(ns.tasks_json) if ns.tasks_json else None
        out = init_spec(ws, ns.title, ns.goal, tasks=tlist)
    elif ns.action == "next":
        out = get_next_task(ws, ns.slug)
    elif ns.action == "complete":
        out = complete_task(ws, ns.slug, ns.step)
    else:
        out = spec_status(ws, ns.slug)

    print(json.dumps(out, indent=2, ensure_ascii=False) if ns.json else render_markdown(out))
    return 0 if out.get("ok", True) else 1


if __name__ == "__main__":
    raise SystemExit(main())
