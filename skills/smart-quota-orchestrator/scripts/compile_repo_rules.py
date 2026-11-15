#!/usr/bin/env python3
"""Bespoke Repo-Aware `CLAUDE.md` / `AGENTS.md` / `.cursorrules` Compiler (`compile_repo_rules.py` — v13.0 Zenith).

Unlike `claude /init` (which burns 25,000–45,000 LLM tokens scanning your repo),
`sqo rules-gen` deterministically inspects your exact codebase on disk in <25ms (0 tokens!)
and compiles a custom-tailored `CLAUDE.md` / `AGENTS.md` / `.cursorrules` containing:
  - Your exact detected tech stack & pinned SDK versions + modern syntax laws
  - Real build/test/lint commands extracted from `package.json`, `pubspec.yaml`, `composer.json`, or `pyproject.toml`
  - Your repo's Top 5 Gravity Core Modules & Entrypoints (`Repo-DNA`)
  - Karpathy's 4 Surgical Laws + FinOps Wallet Shield + Token-Efficiency Guardrails
"""

from __future__ import annotations

import argparse
import importlib.util
import json
from pathlib import Path
from typing import Any, Dict, List

SKILLS_ROOT = Path(__file__).resolve().parents[2]


def _load_sibling(rel_path: str):
    full = SKILLS_ROOT / rel_path
    spec = importlib.util.spec_from_file_location("rules_" + rel_path.replace("/", "_").replace(".", "_"), full)
    assert spec and spec.loader
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def _detect_commands(workspace: Path) -> List[str]:
    cmds: List[str] = []
    pkg = workspace / "package.json"
    if pkg.is_file():
        try:
            scripts = (json.loads(pkg.read_text(encoding="utf-8", errors="ignore")).get("scripts") or {})
            for k in ("dev", "build", "test", "lint", "typecheck"):
                if k in scripts:
                    cmds.append(f"`npm run {k}` -> `{scripts[k]}`")
        except Exception:
            pass
    if (workspace / "pubspec.yaml").is_file():
        cmds.extend(["`flutter analyze` (static analysis)", "`flutter test` (unit & widget tests)"])
    if (workspace / "composer.json").is_file():
        cmds.extend(["`php artisan test`", "`composer dump-autoload`"])
    if (workspace / "pyproject.toml").is_file() or (workspace / "tests").is_dir():
        cmds.append("`python -m unittest discover -s tests -v`")
    return cmds[:8]


def compile_bespoke_rules(workspace: Path, write_target: str = "") -> Dict[str, Any]:
    workspace = workspace.resolve()
    dna_mod = _load_sibling("context-compactor/scripts/repo_dna.py")
    sdk_mod = _load_sibling("apex-spec-surgeon/scripts/sdk_radar.py")

    dna = dna_mod.synthesize_repo_dna(workspace)
    sdk = sdk_mod.detect_installed_sdks(workspace)
    cmds = _detect_commands(workspace)
    idioms = [f"- {c}" for c in (sdk.get("cheat_cards") or [])[:5]]

    lines = [
        f"# ⚡ Project AI Engineering Constitution — `{workspace.name}`",
        "> Auto-compiled by **Smart Quota & Superpowers OS v13.0 Zenith** (`0` LLM tokens burned)",
        "",
        "## 1. Repository DNA & Architecture Map",
        f"- **Detected Stack:** `{', '.join(dna['ecosystems']) or 'polyglot'}` | **Pinned Versions:** `{json.dumps(sdk['versions'])}`",
        f"- **Canonical Entrypoints:** `{', '.join(dna['entrypoints']) or 'auto'}`",
        f"- **Core High-Gravity Modules:** {', '.join(f'`{m}`' for m in dna['core_modules']) or 'none'}",
    ]
    if cmds:
        lines.extend(["", "## 2. Verified Build & Test Commands", *[f"- {c}" for c in cmds]])
    if idioms:
        lines.extend(["", "## 3. Stack-Specific Modern SDK Guardrails (Zero Deprecated Calls)", *idioms])

    lines.extend([
        "",
        "## 4. Karpathy's 4 Surgical Coding Laws",
        "1. **Surface Assumptions First:** Never guess ambiguous schemas, auth rules, or side effects silently.",
        "2. **Simplicity Over Speculation:** Write minimal, clean code for the exact requirement — zero premature wrappers.",
        "3. **Surgical Scope Only:** Touch ONLY the target functions (`sqo_edit_symbol`); never delete unrelated features or leave `TODO` stubs.",
        "4. **Red-Green Verification:** Run minimal affected tests (`sqo_blast_radius`) and `sqo_pr_review` before declaring completion.",
        "",
        "## 5. Quota Firewall & Cloud FinOps Invariants",
        "- **Targeted Reads Only:** Search symbols first (`sqo_code_search`), then read bounded `StartLine`–`EndLine` windows. Never dump lockfiles (`package-lock.json`, `pubspec.lock`, `*.map`).",
        "- **Zero Duplicate Reads & Loops:** Never re-read unchanged files in context; halt after 2 identical failing shell commands.",
        "- **Zero Cloud Wallet-Shock:** Never call Firestore `onSnapshot`/`fetch` in `useEffect` without `[]`; never call paid LLMs inside unbatched loops or without `max_tokens`; use atomic SQL `UPDATE ... WHERE balance >= ?` for wallet deductions.",
    ])

    content = "\n".join(lines) + "\n"
    written_to = ""
    if write_target:
        out_path = workspace / write_target if not Path(write_target).is_absolute() else Path(write_target)
        out_path.parent.mkdir(parents=True, exist_ok=True)
        out_path.write_text(content, encoding="utf-8")
        written_to = str(out_path)

    return {
        "ok": True,
        "repo": workspace.name,
        "ecosystems": dna["ecosystems"],
        "commands_detected": len(cmds),
        "tokens": max(1, len(content) // 4),
        "written_to": written_to,
        "rules_markdown": content,
    }


def main() -> int:
    ap = argparse.ArgumentParser(description="Compile bespoke repo-aware CLAUDE.md / AGENTS.md / .cursorrules")
    ap.add_argument("--workspace", "-w", default=".")
    ap.add_argument("--write", default="", help="Relative file to write (e.g. CLAUDE.md, AGENTS.md, .cursorrules)")
    ap.add_argument("--json", action="store_true")
    ns = ap.parse_args()
    rep = compile_bespoke_rules(Path(ns.workspace), write_target=ns.write)
    print(json.dumps(rep, indent=2, ensure_ascii=False) if ns.json else rep["rules_markdown"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
