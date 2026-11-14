#!/usr/bin/env python3
"""Smart Framework Auto-Detector & 1-Command Workspace Bootstrapper (`sqo init`).

Automatically detects the workspace tech stack (`flutter`, `nextjs`, `laravel`,
`fastapi-python`, `node-ts`, `go`, `rust`, or `generic`) and configures in <100ms:
  1. Framework-specific `.agentignore` / `.cursorignore` / `.claudeignore` rules
     (shielding generated `.g.dart`, `.freezed.dart`, `.next/`, `vendor/`, `Pods/`, etc.)
  2. Cross-IDE `sqo-engine` MCP server wiring
  3. Initial framework architecture memories in `.sqo/memory.db` (idempotent — zero duplicates)
  4. Optional `<40ms` Git pre-commit secret & prompt-tax guard
"""

from __future__ import annotations

import argparse
import importlib.util
import json
import sys
from pathlib import Path
from typing import Any, Dict, List

SKILLS_ROOT = Path(__file__).resolve().parents[2]
SUITE_ROOT = SKILLS_ROOT.parent

PRESETS: Dict[str, Dict[str, Any]] = {
    "flutter": {
        "label": "Flutter / Dart Multi-Platform App",
        "extra_ignores": [
            "# Flutter & codegen token bombs",
            ".dart_tool/",
            "build/",
            "ios/Pods/",
            "ios/Podfile.lock",
            "macos/Pods/",
            "pubspec.lock",
            "*.g.dart",
            "*.freezed.dart",
            "*.gr.dart",
            "*.mocks.dart",
        ],
        "seed_memories": [
            ("build", "Flutter Surgical Verification", "Run targeted widget/unit tests via `flutter test test/<specific>_test.dart` and `dart analyze` instead of full builds."),
            ("gotcha", "Skip Generated Dart Codegen Files", "Never edit or full-read `*.g.dart` or `*.freezed.dart`; inspect the primary `.dart` model/bloc source file."),
        ],
    },
    "nextjs": {
        "label": "Next.js / React Full-Stack App",
        "extra_ignores": [
            "# Next.js & Vercel build caches",
            ".next/",
            ".vercel/",
            "out/",
            "*.tsbuildinfo",
            "next-env.d.ts",
        ],
        "seed_memories": [
            ("arch", "Next.js Route & Server Component Map", "Use `sqo_api_routes` to list all `app/**/route.ts` & `page.tsx` endpoints in 1 step before exploring."),
            ("build", "Targeted Type & Unit Checks", "Prefer `npx tsc --noEmit` + single-file `vitest run <file>` via `sqo denoise`."),
        ],
    },
    "laravel": {
        "label": "Laravel / PHP Web Platform",
        "extra_ignores": [
            "# Laravel caches, vendor & IDE helpers",
            "vendor/",
            "storage/",
            "bootstrap/cache/",
            "_ide_helper.php",
            "_ide_helper_models.php",
            ".phpstorm.meta.php",
            "composer.lock",
        ],
        "seed_memories": [
            ("arch", "Laravel Route & Controller Discovery", "Use `sqo_api_routes` to map `Route::get/post` declarations without scanning `vendor/` or `_ide_helper.php`."),
            ("build", "Targeted Pest / PHPUnit Execution", "Run `php artisan test --filter <TestName>` instead of the entire suite during iteration."),
        ],
    },
    "fastapi-python": {
        "label": "Python / FastAPI / Flask / CLI Project",
        "extra_ignores": [
            "# Python virtualenvs, caches & lockfiles",
            ".venv/",
            "venv/",
            "__pycache__/",
            ".pytest_cache/",
            ".mypy_cache/",
            ".ruff_cache/",
            "poetry.lock",
            "uv.lock",
        ],
        "seed_memories": [
            ("build", "Targeted Python Test Verification", "Use `sqo_blast_radius` to select affected `test_*.py` files and run only those tests."),
        ],
    },
    "node-ts": {
        "label": "Node.js / TypeScript / Vite Project",
        "extra_ignores": [
            "# Node/TS build outputs & lockfiles",
            "node_modules/",
            "dist/",
            "coverage/",
            "*.tsbuildinfo",
        ],
        "seed_memories": [
            ("arch", "TypeScript Symbol & Blast-Radius Workflow", "Use `sqo_code_search` for BM25 symbol lookup and `sqo_blast_radius` before editing shared types."),
        ],
    },
    "go": {
        "label": "Go Backend / Microservice",
        "extra_ignores": ["go.sum", "bin/", "vendor/"],
        "seed_memories": [
            ("build", "Targeted Go Package Testing", "Run `go test ./pkg/<changed_pkg>` instead of `go test ./...` on every small edit."),
        ],
    },
    "rust": {
        "label": "Rust Crate / Workspace",
        "extra_ignores": ["target/", "Cargo.lock"],
        "seed_memories": [
            ("build", "Fast Rust Check Loop", "Prefer `cargo check --message-format=short` over full `cargo build` during code iteration."),
        ],
    },
    "generic": {
        "label": "Polyglot / General Software Workspace",
        "extra_ignores": [],
        "seed_memories": [
            ("arch", "Smart Quota Exploration Protocol", "Use `sqo_code_search` (BM25) and `sqo_smart_outline` (AST) before reading files >250 lines."),
        ],
    },
}


def _load_mod(rel_path: str):
    target = SKILLS_ROOT / rel_path
    spec = importlib.util.spec_from_file_location(rel_path.replace("/", "_"), target)
    assert spec and spec.loader
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def detect_preset(workspace: Path) -> str:
    if (workspace / "pubspec.yaml").is_file():
        return "flutter"
    if any((workspace / f).is_file() for f in ("next.config.js", "next.config.mjs", "next.config.ts")):
        return "nextjs"
    if (workspace / "artisan").is_file() or (workspace / "composer.json").is_file():
        return "laravel"
    if (workspace / "Cargo.toml").is_file():
        return "rust"
    if (workspace / "go.mod").is_file():
        return "go"
    if (workspace / "pyproject.toml").is_file() or (workspace / "requirements.txt").is_file():
        return "fastapi-python"
    if (workspace / "package.json").is_file():
        pkg_txt = (workspace / "package.json").read_text(encoding="utf-8", errors="ignore")
        if '"next"' in pkg_txt:
            return "nextjs"
        return "node-ts"
    return "generic"


def initialize_workspace(
    workspace: Path,
    preset: str = "auto",
    ides: List[str] | None = None,
    with_git_guard: bool = True,
) -> Dict[str, Any]:
    chosen_preset = detect_preset(workspace) if preset == "auto" else preset
    if chosen_preset not in PRESETS:
        chosen_preset = "generic"
    meta = PRESETS[chosen_preset]

    sync_mod = _load_mod("smart-quota-orchestrator/scripts/sync_ide_configs.py")
    mem_mod = _load_mod("project-memory-vault/scripts/memory_vault.py")
    git_mod = _load_mod("smart-quota-orchestrator/scripts/install_git_guard.py")

    # 1. Sync IDEs + append framework-specific ignore rules
    sync_res = sync_mod.sync_workspace_ides(workspace, SUITE_ROOT, ides or ["all"], dry_run=False)
    if meta["extra_ignores"]:
        extra_block = "\n" + "\n".join(meta["extra_ignores"]) + "\n"
        for ig_name in (".agentignore", ".cursorignore", ".claudeignore", ".codeiumignore"):
            ig_path = workspace / ig_name
            if ig_path.is_file():
                cur = ig_path.read_text(encoding="utf-8", errors="ignore")
                if meta["extra_ignores"][0] not in cur:
                    ig_path.write_text(cur + extra_block, encoding="utf-8")

    # 2. Seed idempotent starter architectural memories
    db_path = mem_mod._resolve_db_path(workspace)
    existing_titles = {m["title"] for m in mem_mod.list_facts(db_path, limit=100)}
    seeded_count = 0
    for cat, title, detail in meta["seed_memories"]:
        if title not in existing_titles:
            mem_mod.remember_fact(db_path, cat, title, detail, [])
            seeded_count += 1

    # 3. Install Git pre-commit guard if `.git` exists
    git_guard_installed = False
    if with_git_guard and (workspace / ".git").is_dir():
        g_res = git_mod.install_guard(workspace, SUITE_ROOT)
        git_guard_installed = bool(g_res.get("installed"))

    return {
        "workspace": str(workspace).replace("\\", "/"),
        "detected_preset": chosen_preset,
        "preset_label": meta["label"],
        "synced_ide_files": len(sync_res["synced_files"]),
        "seeded_memories": seeded_count,
        "git_guard_installed": git_guard_installed,
    }


def render_markdown(rep: Dict[str, Any]) -> str:
    return "\n".join([
        f"## 🚀 Workspace Initialized (`{rep['detected_preset']}` — {rep['preset_label']})",
        f"- **Target Workspace**: `{rep['workspace']}`",
        f"- **IDE Configs & Framework Ignore Shields Synced**: `{rep['synced_ide_files']}` file(s)",
        f"- **Starter Memories Seeded into `.sqo/memory.db`**: `{rep['seeded_memories']}` *(auto-injected at `SessionStart`!)*",
        f"- **Git Pre-Commit Secret & Prompt-Tax Guard**: `{'ACTIVE ✅' if rep['git_guard_installed'] else 'Skipped (no .git folder)'}`",
    ])


def main() -> int:
    for s in (sys.stdout, sys.stderr):
        if hasattr(s, "reconfigure"):
            try:
                s.reconfigure(encoding="utf-8")
            except Exception:
                pass

    parser = argparse.ArgumentParser(description="Auto-detect project stack and bootstrap Smart Quota shields, MCP configs & starter memories.")
    parser.add_argument("--workspace", "-w", default=".", help="Target project directory.")
    parser.add_argument("--preset", choices=("auto", *PRESETS.keys()), default="auto", help="Framework preset (default: auto-detect).")
    parser.add_argument("--no-git-guard", action="store_true", help="Skip installing .git/hooks/pre-commit.")
    parser.add_argument("--format", choices=("markdown", "json"), default="markdown", help="Output format.")
    args = parser.parse_args()

    rep = initialize_workspace(Path(args.workspace).resolve(), preset=args.preset, with_git_guard=not args.no_git_guard)
    if args.format == "json":
        print(json.dumps(rep, indent=2, ensure_ascii=False))
    else:
        print(render_markdown(rep))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
