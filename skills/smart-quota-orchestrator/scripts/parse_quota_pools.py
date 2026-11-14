#!/usr/bin/env python3
"""Parse live model quota telemetry into grouped Quota Pools, reset countdowns, and routing advice.

Supports JSON output from Antigravity's `swarm(action="models", all=true)` via
`--input <path>`, `--json-string '<json>'`, or `stdin`.
Zero external dependencies (Python 3.8+ stdlib only).
"""

from __future__ import annotations

import argparse
import datetime as dt
import json
import re
import sys
from typing import Any, Dict, List, Optional, Tuple


def _configure_utf8() -> None:
    for stream in (sys.stdout, sys.stderr):
        if hasattr(stream, "reconfigure"):
            try:
                stream.reconfigure(encoding="utf-8")
            except Exception:
                pass


def _parse_iso_utc(ts: str) -> Optional[dt.datetime]:
    if not ts:
        return None
    cleaned = ts.strip()
    if cleaned.endswith("Z"):
        cleaned = cleaned[:-1] + "+00:00"
    try:
        parsed = dt.datetime.fromisoformat(cleaned)
        if parsed.tzinfo is None:
            parsed = parsed.replace(tzinfo=dt.timezone.utc)
        return parsed.astimezone(dt.timezone.utc)
    except ValueError:
        return None


def _parse_pct(raw: Any) -> Optional[float]:
    if raw is None:
        return None
    if isinstance(raw, (int, float)):
        return float(raw)
    match = re.search(r"(\d+(?:\.\d+)?)", str(raw))
    return float(match.group(1)) if match else None


def _infer_family(model_id: str) -> str:
    lower = model_id.lower()
    if lower.startswith("gemini-") or "orchestrator" in lower:
        return "Google Gemini Pool"
    if lower.startswith("claude-"):
        return "Anthropic Claude Pool"
    if lower.startswith("gpt-"):
        return "OpenAI / GPT-OSS Pool"
    return "Other Model Pool"


def _health_label(pct: Optional[float]) -> str:
    if pct is None:
        return "UNKNOWN"
    if pct <= 0:
        return "EXHAUSTED"
    if pct < 20:
        return "CRITICAL"
    if pct <= 50:
        return "CONSERVE"
    return "HEALTHY"


def _format_countdown(reset_dt: Optional[dt.datetime], now_utc: dt.datetime) -> Tuple[str, Optional[float]]:
    if reset_dt is None:
        return ("Unknown", None)
    delta_sec = (reset_dt - now_utc).total_seconds()
    if delta_sec <= 0:
        return ("Imminent / Refreshing now", 0.0)
    hours = delta_sec / 3600.0
    whole_h = int(delta_sec // 3600)
    mins = int((delta_sec % 3600) // 60)
    if whole_h > 0:
        return (f"{whole_h}h {mins}m", round(hours, 2))
    return (f"{mins}m", round(hours, 2))


def analyze_pools(payload: Dict[str, Any], now_utc: Optional[dt.datetime] = None) -> Dict[str, Any]:
    now = now_utc or dt.datetime.now(dt.timezone.utc)
    display_names: Dict[str, str] = payload.get("display_names") or {}
    quotas: Dict[str, Dict[str, Any]] = payload.get("quotas") or {}
    models: List[str] = payload.get("models") or sorted(quotas.keys())

    grouped: Dict[Tuple[str, str, str], Dict[str, Any]] = {}
    for model_id in models:
        q_info = quotas.get(model_id) or {}
        rem_raw = str(q_info.get("quota_remaining", "unknown"))
        res_raw = str(q_info.get("quota_resets", ""))
        family = _infer_family(model_id)
        key = (family, rem_raw, res_raw)
        if key not in grouped:
            pct = _parse_pct(rem_raw)
            reset_dt = _parse_iso_utc(res_raw)
            countdown_str, hours_left = _format_countdown(reset_dt, now)
            safe_burn_per_hr: Optional[float] = None
            if pct is not None and hours_left is not None and hours_left > 0.05:
                safe_burn_per_hr = round(pct / hours_left, 1)
            grouped[key] = {
                "pool_name": family,
                "quota_remaining": rem_raw,
                "quota_pct": pct,
                "health": _health_label(pct),
                "quota_resets_utc": res_raw or None,
                "time_until_reset": countdown_str,
                "hours_until_reset": hours_left,
                "safe_burn_pct_per_hour": safe_burn_per_hr,
                "quota_note": q_info.get("quota_note"),
                "models": [],
            }
        grouped[key]["models"].append(
            {
                "id": model_id,
                "display_name": display_names.get(model_id, model_id),
            }
        )

    pools = sorted(
        grouped.values(),
        key=lambda p: (0 if "Gemini" in p["pool_name"] else 1, -(p["quota_pct"] or 0.0)),
    )

    recommendations = _build_recommendations(pools)
    return {
        "evaluated_at_utc": now.strftime("%Y-%m-%dT%H:%M:%SZ"),
        "pool_count": len(pools),
        "pools": pools,
        "recommendations": recommendations,
    }


def _build_recommendations(pools: List[Dict[str, Any]]) -> List[str]:
    advice: List[str] = []
    gemini_pool = next((p for p in pools if "Gemini" in p["pool_name"]), None)
    reserve_pools = [p for p in pools if "Gemini" not in p["pool_name"] and (p["quota_pct"] or 0) > 50]

    if gemini_pool:
        pct = gemini_pool["quota_pct"]
        health = gemini_pool["health"]
        ids = {m["id"] for m in gemini_pool["models"]}
        has_orch_carbon = "gemini-pro-orchestrator" in ids
        has_orch_argon = "gemini-pro-orchestrator-argon" in ids

        if health == "HEALTHY":
            if has_orch_carbon:
                advice.append(
                    "Primary Gemini Pool is HEALTHY: Use 'Orchestrator (Carbon)' for complex features to get Carbon planning with Hydrogen execution (~50-60% lower burn than standalone Carbon)."
                )
            advice.append(
                "Reserve standalone 'Gemini 4 Carbon (High)' strictly for deep security audits, architecture design, or subtle bug root-causing."
            )
        elif health == "CONSERVE":
            target = "Orchestrator (Argon)" if has_orch_argon else "Gemini 4 Argon (Medium) / Hydrogen (Medium)"
            advice.append(
                f"Primary Gemini Pool is in CONSERVE mode ({gemini_pool['quota_remaining']} left, resets in {gemini_pool['time_until_reset']}): Prefer '{target}' for interactive coding and delegate multi-file scans via run_workflow(model='flash')."
            )
            if gemini_pool["safe_burn_pct_per_hour"] is not None:
                advice.append(
                    f"Target burn ceiling: <= {gemini_pool['safe_burn_pct_per_hour']}%/hour to reach reset without hitting zero."
                )
        elif health in ("CRITICAL", "EXHAUSTED"):
            hrs = gemini_pool["hours_until_reset"]
            if hrs is not None and hrs <= 0.5 and health != "EXHAUSTED":
                advice.append(
                    f"Gemini Pool is CRITICAL ({gemini_pool['quota_remaining']}) but refreshes soon ({gemini_pool['time_until_reset']}): Use 'Gemini 4 Hydrogen (Low/Medium)' only for quick edits until reset."
                )
            else:
                advice.append(
                    f"Gemini Pool is {health} ({gemini_pool['quota_remaining']}, resets in {gemini_pool['time_until_reset']}): Avoid launching heavy swarms on this pool right now."
                )
            if reserve_pools:
                names = ", ".join(
                    f"{p['pool_name']} ({p['quota_remaining']})" for p in reserve_pools
                )
                advice.append(
                    f"Untouched Failover Reserve Available: {names}. Ask the user if they want to switch to a reserve pool while Gemini refreshes."
                )
    elif pools:
        best = max(pools, key=lambda p: p["quota_pct"] or 0.0)
        advice.append(
            f"Highest available pool is {best['pool_name']} ({best['quota_remaining']} remaining, resets in {best['time_until_reset']})."
        )
    else:
        advice.append("No model quota entries found in input payload.")

    return advice


def render_markdown(report: Dict[str, Any]) -> str:
    lines = [
        "## Live Quota Pool Dashboard",
        "",
        "| Pool | Remaining | Status | Resets In | Safe Burn/hr | Included Models |",
        "| :--- | :--- | :--- | :--- | :--- | :--- |",
    ]
    for pool in report["pools"]:
        burn = (
            f"{pool['safe_burn_pct_per_hour']}%/h"
            if pool["safe_burn_pct_per_hour"] is not None
            else "—"
        )
        sample_names = [m["display_name"] for m in pool["models"]]
        if len(sample_names) > 5:
            models_str = ", ".join(sample_names[:4]) + f" (+{len(sample_names) - 4} more)"
        else:
            models_str = ", ".join(sample_names)
        lines.append(
            f"| **{pool['pool_name']}** | `{pool['quota_remaining']}` | **{pool['health']}** | `{pool['time_until_reset']}` | `{burn}` | {models_str} |"
        )

    lines.extend(["", "### Recommended Routing Strategy", ""])
    for item in report["recommendations"]:
        lines.append(f"- {item}")
    return "\n".join(lines)


def main() -> int:
    _configure_utf8()
    parser = argparse.ArgumentParser(
        description="Analyze AI model quota pools, reset timers, and failover options."
    )
    parser.add_argument("--input", "-i", help="Path to JSON file from swarm(action='models', all=true).")
    parser.add_argument("--json-string", "-j", help="Inline JSON string from swarm(action='models', all=true).")
    parser.add_argument(
        "--format",
        choices=("markdown", "json"),
        default="markdown",
        help="Output format (default: markdown).",
    )
    args = parser.parse_args()

    raw_text = ""
    if args.json_string:
        raw_text = args.json_string
    elif args.input:
        with open(args.input, "r", encoding="utf-8") as fh:
            raw_text = fh.read()
    elif not sys.stdin.isatty():
        raw_text = sys.stdin.read()
    else:
        parser.error("Provide --input <file>, --json-string '<json>', or pipe JSON via stdin.")

    payload = json.loads(raw_text)
    report = analyze_pools(payload)
    if args.format == "json":
        print(json.dumps(report, indent=2, ensure_ascii=False))
    else:
        print(render_markdown(report))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
