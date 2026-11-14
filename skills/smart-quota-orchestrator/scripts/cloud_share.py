#!/usr/bin/env python3
"""Global Cloud Telemetry Publisher & GitHub Profile SVG Trophy Card Generator (`sqo share` / `sqo_cloud_share`).

Connects local Smart Quota OS benchmarks & prevented-token ROI to the official global developer
network at https://sqo.elnemer-ai.com:
  - Computes anonymized efficiency stats (NO source code, file names, or paths ever leave your machine!).
  - Optionally publishes opt-in score to `https://sqo.elnemer-ai.com/api/telemetry.php`.
  - Generates an instant embeddable Cyberpunk GitHub Profile Trophy SVG Card URL:
    `[![Smart Quota Architect](https://sqo.elnemer-ai.com/api/card.php?handle=YOUR_HANDLE)](https://sqo.elnemer-ai.com)`

Zero external dependencies (Python 3.8+ stdlib only).
"""

from __future__ import annotations

import argparse
import importlib.util
import json
import sys
import urllib.parse
import urllib.request
from pathlib import Path
from typing import Any, Dict

SKILLS_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_ENDPOINT = "https://sqo.elnemer-ai.com/api/telemetry.php"
CARD_BASE = "https://sqo.elnemer-ai.com/api/card.php"


def _load_mod(rel_path: str):
    target = SKILLS_ROOT / rel_path
    spec = importlib.util.spec_from_file_location(rel_path.replace("/", "_"), target)
    assert spec and spec.loader
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def build_share_payload(workspace: Path, handle: str = "anonymous-dev") -> Dict[str, Any]:
    bench_mod = _load_mod("smart-quota-orchestrator/scripts/benchmark_suite.py")
    roi_mod = _load_mod("smart-quota-orchestrator/scripts/roi_ledger.py")
    tax_mod = _load_mod("prompt-tax-profiler/scripts/optimize_prompt_rules.py")
    hive_mod = _load_mod("project-memory-vault/scripts/hive_mind.py")

    ws = workspace.resolve()
    bench = bench_mod.run_live_benchmark(ws, SKILLS_ROOT)
    roi = roi_mod.summarize_roi(roi_mod.default_ledger_path())
    tax = tax_mod.profile_workspace(ws)
    stack = hive_mod.detect_stack(ws)

    clean_handle = "".join(c for c in handle.strip() if c.isalnum() or c in "-_")[:28] or "anonymous-dev"
    tokens_saved = max(int(roi["total_tokens_saved"]), int(bench.get("total_before_tokens", 0) - bench.get("total_after_tokens", 0)))
    usd_saved = round((tokens_saved / 1_000_000.0) * 15.0, 2)
    pct = float(bench["average_token_reduction_pct"])
    grade = str(tax["grade"]).split(" ")[0]

    qs = urllib.parse.urlencode(
        {"handle": clean_handle, "saved": tokens_saved, "usd": usd_saved, "pct": pct, "stack": stack, "grade": grade}
    )
    card_url = f"{CARD_BASE}?{qs}"
    profile_card_url = f"{CARD_BASE}?handle={urllib.parse.quote(clean_handle)}"

    return {
        "handle": clean_handle,
        "stack": stack,
        "tokens_saved": tokens_saved,
        "usd_saved": usd_saved,
        "compression_pct": pct,
        "grade": grade,
        "live_card_url": card_url,
        "profile_card_url": profile_card_url,
        "markdown_embed": f"[![Smart Quota OS Trophy]({card_url})](https://sqo.elnemer-ai.com)",
    }


def publish_telemetry(payload: Dict[str, Any], endpoint: str = DEFAULT_ENDPOINT) -> Dict[str, Any]:
    body = json.dumps(
        {
            "handle": payload["handle"],
            "stack": payload["stack"],
            "tokens_saved": payload["tokens_saved"],
            "usd_saved": payload["usd_saved"],
            "compression_pct": payload["compression_pct"],
            "grade": payload["grade"],
        }
    ).encode("utf-8")
    req = urllib.request.Request(
        endpoint,
        data=body,
        headers={"Content-Type": "application/json", "User-Agent": "SmartQuotaOS/8.0"},
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=6) as resp:
            return {"published": True, "server_response": json.loads(resp.read().decode("utf-8", errors="replace"))}
    except Exception as exc:
        return {"published": False, "offline_fallback": True, "reason": str(exc)}


def main() -> int:
    for s in (sys.stdout, sys.stderr):
        if hasattr(s, "reconfigure"):
            try:
                s.reconfigure(encoding="utf-8")
            except Exception:
                pass
    parser = argparse.ArgumentParser(description="Generate your GitHub Profile SVG Trophy Card & publish opt-in global ROI stats.")
    parser.add_argument("--workspace", "-w", default=".", help="Workspace path.")
    parser.add_argument("--handle", default="ElNeMeR", help="Developer GitHub/X handle.")
    parser.add_argument("--publish", action="store_true", help="Opt-in publish anonymized score to sqo.elnemer-ai.com leaderboard.")
    parser.add_argument("--format", choices=("markdown", "json"), default="markdown")
    args = parser.parse_args()

    payload = build_share_payload(Path(args.workspace), handle=args.handle)
    pub_res = publish_telemetry(payload) if args.publish else {"published": False}
    payload["cloud_sync"] = pub_res

    if args.format == "json":
        print(json.dumps(payload, indent=2, ensure_ascii=False))
    else:
        print(f"## 🏆 Smart Quota Global Trophy Card for `@{payload['handle']}`")
        print(f"- **Stack**: `{payload['stack']}` | **Compression**: `-{payload['compression_pct']}%` | **Grade**: `{payload['grade']}` | **Saved**: `{payload['tokens_saved']:,}` tok (`${payload['usd_saved']}`)")
        if args.publish:
            print(f"- **Global Leaderboard Sync**: `{'LIVE ON sqo.elnemer-ai.com!' if pub_res.get('published') else 'Offline URL Card Ready'}`")
        print("\n### Paste into your GitHub Profile `README.md`:")
        print(f"```markdown\n{payload['markdown_embed']}\n```")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
