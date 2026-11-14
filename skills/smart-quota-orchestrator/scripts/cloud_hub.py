#!/usr/bin/env python3
"""Global Community Preset & Golden-Rule Cloud Hub Client (`sqo hub` / `sqo_cloud_hub`).

Connects any workspace to the global Smart Quota Community Hub at `https://sqo.elnemer-ai.com/api/presets.php`:
  - `list`    : Browse battle-tested Golden AI Rules & Gotchas across Flutter, Next.js, Laravel, FastAPI, Rust & Go.
  - `pull`    : Pull verified golden gotchas for your stack directly into your local Memory Vault + Hive-Mind!
  - `publish` : Opt-in share a secret-scrubbed architectural tip with developers worldwide!

Includes complete offline built-in curated presets so it works 100% offline in tests and air-gapped networks.
"""

from __future__ import annotations

import argparse
import importlib.util
import json
import sys
import urllib.parse
import urllib.request
from pathlib import Path
from typing import Any, Dict, List

SKILLS_ROOT = Path(__file__).resolve().parents[2]
HUB_URL = "https://sqo.elnemer-ai.com/api/presets.php"

BUILTIN_PRESETS: List[Dict[str, Any]] = [
    {
        "stack": "flutter",
        "title": "Isolate Riverpod/Bloc Codegen & Build Artifacts",
        "rule": "Never read *.g.dart, *.freezed.dart, pubspec.lock, or .dart_tool/; inspect source models and run dart analyze on modified files only.",
        "author": "ElNeMeR",
    },
    {
        "stack": "nextjs",
        "title": "Next.js 15 App Router Server/Client Boundary Discipline",
        "rule": "Keep async DB/env logic in Server Components or Route Handlers; never read .next/ or package-lock.json; use sqo_api_routes first.",
        "author": "ElNeMeR",
    },
    {
        "stack": "laravel",
        "title": "Distill Migrations & Skip Vendor/IDE-Helper Dumps",
        "rule": "Run sqo_schema_distill instead of reading database/migrations/*.php; block _ide_helper.php and composer.lock.",
        "author": "ElNeMeR",
    },
    {
        "stack": "python",
        "title": "Zero-Bloat FastAPI & Async Type Safety",
        "rule": "Extract Pydantic/SQLAlchemy schemas via sqo_schema_distill and validate edits with sqo_shadow_check (<12ms AST parse) before pytest.",
        "author": "ElNeMeR",
    },
]


def _load(rel: str):
    p = SKILLS_ROOT / rel
    spec = importlib.util.spec_from_file_location(rel.replace("/", "_"), p)
    assert spec and spec.loader
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


def fetch_hub_presets(stack: str = "", online: bool = True) -> Dict[str, Any]:
    items = BUILTIN_PRESETS
    source = "builtin_offline"
    if online:
        qs = f"?stack={urllib.parse.quote(stack)}" if stack and stack != "all" else ""
        try:
            req = urllib.request.Request(HUB_URL + qs, headers={"User-Agent": "SmartQuotaOS/9.0"})
            with urllib.request.urlopen(req, timeout=5) as resp:
                data = json.loads(resp.read().decode("utf-8", errors="replace"))
                if data.get("ok") and isinstance(data.get("presets"), list):
                    items = data["presets"]
                    source = "live_cloud_hub"
        except Exception:
            pass
    if stack and stack not in ("all", "auto"):
        items = [x for x in items if x.get("stack") in (stack.lower(), "universal")]
    return {"source": source, "count": len(items), "presets": items}


def pull_into_workspace(workspace: Path, stack: str = "auto", online: bool = True) -> Dict[str, Any]:
    ws = workspace.resolve()
    hive_mod = _load("project-memory-vault/scripts/hive_mind.py")
    mem_mod = _load("project-memory-vault/scripts/memory_vault.py")

    resolved_stack = hive_mod.detect_stack(ws) if stack == "auto" else stack.lower()
    fetched = fetch_hub_presets(resolved_stack, online=online)
    local_db = mem_mod._resolve_db_path(ws)

    imported = 0
    for p in fetched["presets"]:
        mem_mod.remember_fact(
            local_db,
            category=f"hub:{p.get('stack', resolved_stack)}",
            title=str(p["title"]),
            detail=str(p["rule"]),
            files=[],
        )
        imported += 1
    return {"workspace": ws.name, "stack": resolved_stack, "source": fetched["source"], "imported_rules": imported}


def publish_hub_rule(stack: str, title: str, rule: str, author: str = "ElNeMeR") -> Dict[str, Any]:
    scrub_mod = _load("project-memory-vault/scripts/scrub_secrets.py")
    clean_rule = scrub_mod.scrub_text(rule)["scrubbed_text"]
    body = json.dumps({"stack": stack, "title": title, "rule": clean_rule, "author": author}).encode("utf-8")
    req = urllib.request.Request(
        HUB_URL,
        data=body,
        headers={"Content-Type": "application/json", "User-Agent": "SmartQuotaOS/9.0"},
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=6) as resp:
            return {"published": True, "response": json.loads(resp.read().decode("utf-8", errors="replace"))}
    except Exception as exc:
        return {"published": False, "reason": str(exc)}


def main() -> int:
    for s in (sys.stdout, sys.stderr):
        if hasattr(s, "reconfigure"):
            try:
                s.reconfigure(encoding="utf-8")
            except Exception:
                pass
    parser = argparse.ArgumentParser(description="Smart Quota Global Cloud Preset & Golden-Rule Hub.")
    parser.add_argument("action", choices=("list", "pull", "publish"), nargs="?", default="list")
    parser.add_argument("--workspace", "-w", default=".", help="Workspace root.")
    parser.add_argument("--stack", default="auto", help="Stack filter.")
    parser.add_argument("--title", default="", help="Rule title for publish.")
    parser.add_argument("--rule", default="", help="Golden rule content for publish.")
    parser.add_argument("--author", default="ElNeMeR", help="Author handle.")
    parser.add_argument("--offline", action="store_true", help="Use offline built-in catalog only.")
    args = parser.parse_args()

    if args.action == "pull":
        res = pull_into_workspace(Path(args.workspace), stack=args.stack, online=not args.offline)
    elif args.action == "publish":
        res = publish_hub_rule(args.stack, args.title, args.rule, author=args.author)
    else:
        st = "" if args.stack in ("auto", "all") else args.stack
        res = fetch_hub_presets(st, online=not args.offline)
    print(json.dumps(res, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
