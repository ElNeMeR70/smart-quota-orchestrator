#!/usr/bin/env python3
"""Quadratic Context-Rot Early-Warning & Auto-Handoff Monitor (`sqo context-health`).

Because LLM conversation history grows quadratically in cumulative billed tokens
(Turn N re-sends Turns 1..N-1), sessions past ~28 heavy tool steps quietly cost
4x-8x more quota per edit and suffer attention dilution ("Context Rot").

Inspects the active session transcript (or estimated turn/size metrics), scores
Context Rot Risk (0-100), recommends whether to continue or `/compact` / warm-restart,
and emits an instant <350-token Zero-Loss Handoff Brief!
"""

from __future__ import annotations

import argparse
import importlib.util
import json
import sys
from pathlib import Path
from typing import Any, Dict, Optional

SKILLS_ROOT = Path(__file__).resolve().parents[2]


def _load_mod(rel_path: str):
    target = SKILLS_ROOT / rel_path
    spec = importlib.util.spec_from_file_location(rel_path.replace("/", "_"), target)
    assert spec and spec.loader
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def _find_latest_transcript() -> Optional[Path]:
    brain_root = Path.home() / ".gemini" / "antigravity" / "brain"
    if not brain_root.is_dir():
        return None
    candidates = list(brain_root.glob("*/.system_generated/logs/transcript.jsonl"))
    if not candidates:
        return None
    return max(candidates, key=lambda p: p.stat().st_mtime_ns)


def evaluate_context_health(
    workspace: Path,
    transcript_path: Optional[Path] = None,
    goal: str = "Continue active implementation seamlessly",
) -> Dict[str, Any]:
    t_path = transcript_path or _find_latest_transcript()
    step_count = 0
    approx_window_tokens = 0
    tool_calls_total = 0

    if t_path and t_path.is_file():
        raw_bytes = t_path.stat().st_size
        approx_window_tokens = int(raw_bytes / 4)
        for line in t_path.read_text(encoding="utf-8", errors="ignore").splitlines():
            if not line.strip():
                continue
            step_count += 1
            try:
                obj = json.loads(line)
                tool_calls_total += len(obj.get("tool_calls") or [])
            except Exception:
                pass

    # Compute Context-Rot Score (0 = crisp fresh context, 100 = severe quadratic bloat)
    tok_pressure = min(65.0, (approx_window_tokens / 120_000.0) * 65.0)
    turn_pressure = min(35.0, (step_count / 70.0) * 35.0)
    rot_score = int(round(tok_pressure + turn_pressure))

    if rot_score >= 70:
        status = "ROT_CRITICAL — Run `/compact` or start a warm session NOW (save ~65% per-turn quota!)"
    elif rot_score >= 40:
        status = "MODERATE_GROWTH — Finish current atomic task, then `/compact` before starting the next feature"
    else:
        status = "CRISP_OPTIMAL — Context window is lean and KV-cache efficient"

    handoff_mod = _load_mod("context-compactor/scripts/build_handoff_brief.py")
    brief_data = handoff_mod.build_brief(workspace, goal, ["Verify tests and continue from clean compacted state"])
    brief_md = handoff_mod.render_markdown(brief_data)

    return {
        "transcript_inspected": str(t_path).replace("\\", "/") if t_path else "(none)",
        "trajectory_steps": step_count,
        "tool_calls_count": tool_calls_total,
        "approx_context_tokens": approx_window_tokens,
        "context_rot_score": rot_score,
        "status": status,
        "ready_handoff_brief": brief_md,
    }


def render_markdown(rep: Dict[str, Any]) -> str:
    lines = [
        "## 🧠 Session Context-Rot & Quadratic Burn Health",
        f"- **Context-Rot Risk Score**: **`{rep['context_rot_score']} / 100`** — **{rep['status']}**",
        f"- **Trajectory Volume**: `{rep['trajectory_steps']}` steps • `{rep['tool_calls_count']}` tool calls • `~{rep['approx_context_tokens']:,}` context tokens",
        "",
        "### Ready-to-Use `<350`-Token Zero-Loss Handoff Snapshot",
        rep["ready_handoff_brief"],
    ]
    return "\n".join(lines)


def main() -> int:
    for s in (sys.stdout, sys.stderr):
        if hasattr(s, "reconfigure"):
            try:
                s.reconfigure(encoding="utf-8")
            except Exception:
                pass

    parser = argparse.ArgumentParser(description="Measure session Context-Rot risk and emit a zero-loss handoff snapshot.")
    parser.add_argument("--workspace", "-w", default=".", help="Workspace root.")
    parser.add_argument("--transcript", "-t", default=None, help="Optional explicit transcript.jsonl path.")
    parser.add_argument("--goal", "-g", default="Continue active feature cleanly", help="Current objective for handoff brief.")
    parser.add_argument("--format", choices=("markdown", "json"), default="markdown", help="Output format.")
    args = parser.parse_args()

    tp = Path(args.transcript).resolve() if args.transcript else None
    rep = evaluate_context_health(Path(args.workspace).resolve(), transcript_path=tp, goal=args.goal)
    if args.format == "json":
        print(json.dumps(rep, indent=2, ensure_ascii=False))
    else:
        print(render_markdown(rep))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
