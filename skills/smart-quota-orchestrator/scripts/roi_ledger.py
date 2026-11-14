#!/usr/bin/env python3
"""Persistent Token & Dollar ($USD) ROI Telemetry Ledger (`sqo roi`).

Tracks every single token saved automatically by the 3-Stage Stateful Hook Shield
(`token_shield_hook.py`) and MCP/CLI compression engines in a tiny SQLite database,
and calculates real-world API dollar equivalents across Frontier, Balanced, and Flash models.

Zero external dependencies (Python 3.8+ stdlib + built-in sqlite3).
"""

from __future__ import annotations

import argparse
import datetime as dt
import json
import os
import sqlite3
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional

# Approximate input $/1M tokens across major model tiers for transparent ROI reporting
PRICING_PER_1M_USD = {
    "frontier_opus_pro": {"label": "Frontier Tier ($15.00 / 1M tok — Opus / Heavy Reasoning)", "usd_per_1m": 15.00},
    "balanced_sonnet_carbon": {"label": "Balanced Pro Tier ($3.00 / 1M tok — Sonnet / Carbon / Pro)", "usd_per_1m": 3.00},
    "fast_flash_hydrogen": {"label": "Fast Execution Tier ($0.30 / 1M tok — Flash / Hydrogen)", "usd_per_1m": 0.30},
}


def _configure_utf8() -> None:
    for stream in (sys.stdout, sys.stderr):
        if hasattr(stream, "reconfigure"):
            try:
                stream.reconfigure(encoding="utf-8")
            except Exception:
                pass


def default_ledger_path(explicit_db: Optional[str] = None) -> Path:
    if explicit_db:
        p = Path(explicit_db).resolve()
        p.parent.mkdir(parents=True, exist_ok=True)
        return p
    base = os.environ.get("PLUGIN_DATA")
    if base:
        root = Path(base)
    else:
        root = Path.home() / ".gemini" / "antigravity" / "plugin_data" / "smart-quota-orchestrator"
    root.mkdir(parents=True, exist_ok=True)
    return root / "roi_ledger.db"


def _connect(db_path: Path) -> sqlite3.Connection:
    db_path.parent.mkdir(parents=True, exist_ok=True)
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
    return con


def record_saving(
    event_type: str,
    tokens_saved: int,
    target: str = "",
    conv_id: str = "",
    db_path: Optional[Path] = None,
) -> None:
    if tokens_saved <= 0:
        return
    path = db_path or default_ledger_path()
    now = dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    try:
        con = _connect(path)
        con.execute(
            "INSERT INTO savings_events(ts_utc, event_type, target, tokens_saved, conv_id) VALUES (?, ?, ?, ?, ?)",
            (now, event_type, target[:200], int(tokens_saved), conv_id[:80]),
        )
        con.commit()
        con.close()
    except Exception:
        pass


def summarize_roi(db_path: Optional[Path] = None) -> Dict[str, Any]:
    path = db_path or default_ledger_path()
    con = _connect(path)
    today_prefix = dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%d")

    total_row = con.execute("SELECT COUNT(*), COALESCE(SUM(tokens_saved), 0) FROM savings_events").fetchone()
    today_row = con.execute(
        "SELECT COUNT(*), COALESCE(SUM(tokens_saved), 0) FROM savings_events WHERE ts_utc LIKE ?",
        (f"{today_prefix}%",),
    ).fetchone()
    by_type_rows = con.execute(
        """
        SELECT event_type, COUNT(*), SUM(tokens_saved)
        FROM savings_events
        GROUP BY event_type
        ORDER BY SUM(tokens_saved) DESC
        """
    ).fetchall()
    recent_rows = con.execute(
        "SELECT ts_utc, event_type, target, tokens_saved FROM savings_events ORDER BY id DESC LIMIT 10"
    ).fetchall()
    con.close()

    total_events = int(total_row[0] or 0)
    total_tokens = int(total_row[1] or 0)
    today_events = int(today_row[0] or 0)
    today_tokens = int(today_row[1] or 0)

    usd_estimates = {
        k: {
            "label": meta["label"],
            "saved_usd": round((total_tokens / 1_000_000.0) * meta["usd_per_1m"], 4),
            "today_usd": round((today_tokens / 1_000_000.0) * meta["usd_per_1m"], 4),
        }
        for k, meta in PRICING_PER_1M_USD.items()
    }

    return {
        "ledger_db": str(path).replace("\\", "/"),
        "total_interceptions": total_events,
        "total_tokens_saved": total_tokens,
        "today_interceptions": today_events,
        "today_tokens_saved": today_tokens,
        "usd_equivalents": usd_estimates,
        "by_defense_layer": [
            {"event_type": r[0], "count": int(r[1]), "tokens_saved": int(r[2])}
            for r in by_type_rows
        ],
        "recent_events": [
            {"ts_utc": r[0], "event_type": r[1], "target": r[2], "tokens_saved": int(r[3])}
            for r in recent_rows
        ],
    }


def render_markdown(rep: Dict[str, Any]) -> str:
    bal = rep["usd_equivalents"]["balanced_sonnet_carbon"]
    front = rep["usd_equivalents"]["frontier_opus_pro"]
    lines = [
        "## 💰 Smart Quota Live ROI & Token-Savings Ledger",
        f"- **All-Time Prevented Waste**: **`{rep['total_tokens_saved']:,}` tokens** across `{rep['total_interceptions']}` autonomous interceptions",
        f"- **Today's Prevented Waste (UTC)**: **`{rep['today_tokens_saved']:,}` tokens** (`{rep['today_interceptions']}` event(s))",
        f"- **Estimated API Cost Saved**: **`${bal['saved_usd']:.2f}`** (Balanced Tier) — up to **`${front['saved_usd']:.2f}`** (Frontier Opus Tier)",
        "",
    ]
    if rep["by_defense_layer"]:
        lines.extend([
            "### Savings Breakdown by Autonomous Shield Layer",
            "",
            "| Defense Layer | Interceptions | Prevented Tokens |",
            "| :--- | :--- | :--- |",
        ])
        for row in rep["by_defense_layer"]:
            lines.append(f"| `{row['event_type']}` | `{row['count']}` | **`{row['tokens_saved']:,}`** |")
    else:
        lines.append("_No blocked bombs or compressed calls recorded yet — active shield is armed and monitoring!_")
    return "\n".join(lines)


def main() -> int:
    _configure_utf8()
    parser = argparse.ArgumentParser(description="Inspect or record cumulative token & $USD savings in the ROI Ledger.")
    parser.add_argument("--db", default=None, help="Optional custom SQLite ledger path.")
    parser.add_argument("--record", nargs=3, metavar=("EVENT_TYPE", "TOKENS", "TARGET"), help="Record a custom saving event.")
    parser.add_argument("--format", choices=("markdown", "json"), default="markdown", help="Output format.")
    args = parser.parse_args()

    db_p = default_ledger_path(args.db)
    if args.record:
        ev_type, tok_str, target = args.record
        record_saving(ev_type, int(tok_str), target=target, db_path=db_p)

    rep = summarize_roi(db_p)
    if args.format == "json":
        print(json.dumps(rep, indent=2, ensure_ascii=False))
    else:
        print(render_markdown(rep))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
