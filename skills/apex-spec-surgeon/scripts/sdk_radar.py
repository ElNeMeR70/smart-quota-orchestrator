#!/usr/bin/env python3
"""Context7-Class Live Version-Pinned SDK Idioms & Deprecation Radar (v10.0 Apex).

Reads exact package versions from package.json, pubspec.yaml, pyproject.toml,
requirements.txt & composer.json, surfaces <250-token Modern SDK Cheat-Cards,
and scans workspace code for deprecated 2023/2024 API hallucinations!
"""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from typing import Any, Dict, List, Set

DEPRECATION_RULES = [
    {
        "id": "flutter-willpopscope",
        "ecosystems": {"flutter"},
        "exts": {".dart"},
        "pattern": re.compile(r"\bWillPopScope\s*\("),
        "deprecated": "WillPopScope(...)",
        "modern_fix": "Use `PopScope(canPop: ..., onPopInvokedWithResult: (didPop, result) { ... })` (Flutter 3.22+).",
    },
    {
        "id": "flutter-withopacity",
        "ecosystems": {"flutter"},
        "exts": {".dart"},
        "pattern": re.compile(r"\.withOpacity\s*\("),
        "deprecated": "color.withOpacity(x)",
        "modern_fix": "Use `color.withValues(alpha: x)` to avoid wide-gamut precision loss (Flutter 3.27+).",
    },
    {
        "id": "google-legacy-genai",
        "ecosystems": {"python", "nextjs", "node"},
        "exts": {".py", ".ts", ".tsx", ".js"},
        "pattern": re.compile(r"(?:\bimport\s+google\.generativeai\b|\bfrom\s+google\s+import\s+generativeai\b|@google/generative-ai)"),
        "deprecated": "google-generativeai / @google/generative-ai",
        "modern_fix": "Use unified SDK `from google import genai` (`google-genai`) or `@google/genai` with `client.models.generate_content(...)`.",
    },
    {
        "id": "openai-v0-chatcompletion",
        "ecosystems": {"python"},
        "exts": {".py"},
        "pattern": re.compile(r"\bopenai\.ChatCompletion\.create\s*\("),
        "deprecated": "openai.ChatCompletion.create(...)",
        "modern_fix": "Use OpenAI v1+ client: `OpenAI().chat.completions.create(...)` or `responses.create(...)`.",
    },
    {
        "id": "pydantic-v1-dict",
        "ecosystems": {"python"},
        "exts": {".py"},
        "pattern": re.compile(r"\bclass\s+Config\s*:|\.(?:parse_obj|from_orm)\s*\("),
        "deprecated": "Pydantic v1 `class Config:` / `.parse_obj()` / `.from_orm()`",
        "modern_fix": "Use Pydantic v2 `model_config = ConfigDict(...)`, `Model.model_validate(...)`, and `model.model_dump()`.",
    },
    {
        "id": "fastapi-on-event",
        "ecosystems": {"python"},
        "exts": {".py"},
        "pattern": re.compile(r"@\w+\.on_event\s*\(\s*['\"](?:startup|shutdown)['\"]\s*\)"),
        "deprecated": "@app.on_event('startup' | 'shutdown')",
        "modern_fix": "Use `@asynccontextmanager async def lifespan(app: FastAPI): yield` passed to `FastAPI(lifespan=lifespan)`.",
    },
    {
        "id": "tailwind-v4-directives",
        "ecosystems": {"tailwind-v4"},
        "exts": {".css", ".scss"},
        "pattern": re.compile(r"@tailwind\s+(?:base|components|utilities)\s*;"),
        "deprecated": "@tailwind base; @tailwind utilities;",
        "modern_fix": "Tailwind CSS v4 uses `@import \"tailwindcss\";` and `@theme { ... }` instead of `@tailwind` directives.",
    },
]

STACK_CHEAT_CARDS = {
    "flutter": "Flutter Modern Idioms: use `PopScope` (`onPopInvokedWithResult`), `Color.withValues(alpha:)`, Dart 3 sealed classes/pattern matching, and `flutter pub add`.",
    "nextjs-15+": "Next.js 15+ Breaking Rules: `params`, `searchParams`, `cookies()`, and `headers()` are ASYNC (`await params`)! `fetch()` is uncached by default.",
    "tailwind-v4": "Tailwind v4 Rules: replace `@tailwind` directives with `@import \"tailwindcss\";`; configure tokens via CSS `@theme {}` instead of `tailwind.config.js`.",
    "python": "Modern Python AI/API Idioms: use `google-genai` (`from google import genai`), Pydantic v2 (`model_validate` / `model_dump`), and FastAPI `lifespan`.",
    "laravel": "Laravel 11/12 Rules: middleware & exceptions live in `bootstrap/app.php` (no `Http/Kernel.php`); schedules live in `routes/console.php`.",
}


def detect_installed_sdks(workspace: Path) -> Dict[str, Any]:
    workspace = workspace.resolve()
    ecosystems: Set[str] = set()
    versions: Dict[str, str] = {}

    pkg_json = workspace / "package.json"
    if pkg_json.is_file():
        ecosystems.add("node")
        try:
            data = json.loads(pkg_json.read_text(encoding="utf-8", errors="ignore"))
            deps = {**(data.get("dependencies") or {}), **(data.get("devDependencies") or {})}
            for k in ("next", "react", "tailwindcss", "@google/genai", "openai", "zod", "prisma"):
                if k in deps:
                    versions[k] = str(deps[k])
            if "next" in deps:
                ecosystems.add("nextjs")
                if re.search(r"(?:^|[^\d])(?:15|16)\.", str(deps["next"])):
                    ecosystems.add("nextjs-15+")
            if "tailwindcss" in deps and re.search(r"(?:^|[^\d])4\.", str(deps["tailwindcss"])):
                ecosystems.add("tailwind-v4")
        except Exception:
            pass

    pubspec = workspace / "pubspec.yaml"
    if pubspec.is_file():
        ecosystems.add("flutter")
        txt = pubspec.read_text(encoding="utf-8", errors="ignore")
        for m in re.finditer(r"^\s*(flutter_riverpod|go_router|dio|Drift|bloc|flutter_bloc)\s*:\s*([^\s#]+)", txt, re.MULTILINE):
            versions[m.group(1)] = m.group(2)

    if (workspace / "pyproject.toml").is_file() or (workspace / "requirements.txt").is_file():
        ecosystems.add("python")

    if (workspace / "composer.json").is_file():
        ecosystems.add("laravel")

    if not ecosystems:
        # Fallback by file extensions present
        for p in workspace.rglob("*"):
            if p.is_file():
                if p.suffix == ".dart":
                    ecosystems.add("flutter")
                elif p.suffix == ".py":
                    ecosystems.add("python")
                elif p.suffix in (".ts", ".tsx"):
                    ecosystems.add("node")
                if len(ecosystems) >= 2:
                    break

    cards = [STACK_CHEAT_CARDS[k] for k in STACK_CHEAT_CARDS if k in ecosystems]
    return {"ecosystems": sorted(ecosystems), "versions": versions, "cheat_cards": cards}


def scan_sdk_deprecations(workspace: Path) -> Dict[str, Any]:
    workspace = workspace.resolve()
    info = detect_installed_sdks(workspace)
    active_ecos = set(info["ecosystems"])
    skip_dirs = {".git", "node_modules", ".venv", "venv", "__pycache__", "build", "dist", ".next", ".dart_tool", "vendor", ".sqo", "tests"}

    hits: List[Dict[str, Any]] = []
    for p in workspace.rglob("*"):
        if not p.is_file() or any(part in skip_dirs for part in p.parts):
            continue
        ext = p.suffix.lower()
        applicable = [
            r for r in DEPRECATION_RULES
            if ext in r["exts"] and (not r["ecosystems"] or (r["ecosystems"] & active_ecos) or ext in {".dart", ".py"})
        ]
        if not applicable:
            continue
        try:
            text = p.read_text(encoding="utf-8", errors="ignore")
        except OSError:
            continue
        for ln_no, ln in enumerate(text.splitlines(), 1):
            for rule in applicable:
                if rule["pattern"].search(ln):
                    hits.append(
                        {
                            "rule_id": rule["id"],
                            "file": str(p.relative_to(workspace)).replace("\\", "/"),
                            "line": ln_no,
                            "deprecated": rule["deprecated"],
                            "modern_fix": rule["modern_fix"],
                        }
                    )
                    if len(hits) >= 30:
                        break
        if len(hits) >= 30:
            break

    return {
        "clean": len(hits) == 0,
        "ecosystems": info["ecosystems"],
        "detected_versions": info["versions"],
        "cheat_cards": info["cheat_cards"],
        "deprecation_count": len(hits),
        "deprecations": hits,
    }


def render_markdown(rep: Dict[str, Any]) -> str:
    lines = [
        f"### 📚 SDK Version & Anti-Deprecation Radar ({', '.join(rep['ecosystems']) or 'generic'})",
        f"- **Pinned Versions:** `{json.dumps(rep['detected_versions'])}`",
    ]
    for c in rep["cheat_cards"]:
        lines.append(f"- 💡 {c}")
    if rep["deprecations"]:
        lines.append(f"\n#### ⚠️ Deprecated API Calls Found ({rep['deprecation_count']})")
        for d in rep["deprecations"]:
            lines.append(f"- `{d['file']}:L{d['line']}` uses `{d['deprecated']}` -> **{d['modern_fix']}**")
    else:
        lines.append("- ✅ **Zero deprecated SDK calls detected!**")
    return "\n".join(lines)


def main() -> int:
    ap = argparse.ArgumentParser(description="Live Version-Pinned SDK & Anti-Deprecation Radar")
    ap.add_argument("--workspace", default=".")
    ap.add_argument("--json", action="store_true")
    ns = ap.parse_args()
    rep = scan_sdk_deprecations(Path(ns.workspace))
    print(json.dumps(rep, indent=2, ensure_ascii=False) if ns.json else render_markdown(rep))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
