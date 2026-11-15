#!/usr/bin/env python3
"""Environment Variable & Cross-Layer Configuration Drift Detector (`detect_drift.py` — v11.0 Hypernova).

Prevents silent production boot crashes by scanning all `os.getenv()`, `os.environ[]`,
`process.env.*`, `import.meta.env.*`, `env()`, and `String.fromEnvironment()` references
across the codebase and cross-checking them against `.env` and `.env.example`!
"""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from typing import Any, Dict, List, Set

ENV_CODE_PATTERNS = [
    re.compile(r"\bos\.getenv\s*\(\s*['\"]([A-Z][A-Z0-9_]{2,})['\"]"),
    re.compile(r"\bos\.environ(?:\.get)?\s*[\(\[]\s*['\"]([A-Z][A-Z0-9_]{2,})['\"]"),
    re.compile(r"\bprocess\.env\.([A-Z][A-Z0-9_]{2,})\b"),
    re.compile(r"\bimport\.meta\.env\.([A-Z][A-Z0-9_]{2,})\b"),
    re.compile(r"\benv\s*\(\s*['\"]([A-Z][A-Z0-9_]{2,})['\"]"),
    re.compile(r"\b(?:String|int|bool)\.fromEnvironment\s*\(\s*['\"]([A-Z][A-Z0-9_]{2,})['\"]"),
]

SYSTEM_STD_ENVS = {
    "PATH", "HOME", "USER", "SHELL", "PWD", "TERM", "LANG", "NODE_ENV", "CI",
    "PORT", "TZ", "TEMP", "TMP", "APPDATA", "LOCALAPPDATA", "USERPROFILE",
    "PYTHONIOENCODING", "PYTHONPATH", "GITHUB_ACTIONS",
}

SKIP_DIRS = {".git", "node_modules", ".venv", "venv", "__pycache__", "build", "dist", ".next", ".dart_tool", "vendor", ".sqo", "tests"}


def _parse_env_keys(env_file: Path) -> Set[str]:
    if not env_file.is_file():
        return set()
    keys: Set[str] = set()
    for ln in env_file.read_text(encoding="utf-8", errors="ignore").splitlines():
        s = ln.strip()
        if not s or s.startswith("#"):
            continue
        if s.startswith("export "):
            s = s[7:].strip()
        if "=" in s:
            k = s.split("=", 1)[0].strip()
            if re.match(r"^[A-Za-z_][A-Za-z0-9_]*$", k):
                keys.add(k)
    return keys


def audit_env_and_config_drift(workspace: Path) -> Dict[str, Any]:
    workspace = workspace.resolve()
    example_keys: Set[str] = set()
    for candidate in (".env.example", ".env.sample", ".env.template"):
        example_keys |= _parse_env_keys(workspace / candidate)
    local_env_keys = _parse_env_keys(workspace / ".env") | _parse_env_keys(workspace / ".env.local")

    referenced: Dict[str, List[str]] = {}
    exts = {".py", ".ts", ".tsx", ".js", ".jsx", ".php", ".dart", ".go", ".rs"}

    for p in workspace.rglob("*"):
        if not p.is_file() or p.suffix.lower() not in exts:
            continue
        if any(part in SKIP_DIRS for part in p.parts) or p.name == "detect_drift.py":
            continue
        try:
            txt = p.read_text(encoding="utf-8", errors="ignore")
        except OSError:
            continue
        rel = str(p.relative_to(workspace)).replace("\\", "/")
        for pat in ENV_CODE_PATTERNS:
            for m in pat.finditer(txt):
                key = m.group(1)
                if key in SYSTEM_STD_ENVS:
                    continue
                referenced.setdefault(key, [])
                if rel not in referenced[key]:
                    referenced[key].append(rel)

    missing_in_example = sorted(k for k in referenced if example_keys and k not in example_keys)
    undocumented_all = sorted(k for k in referenced if not example_keys and not local_env_keys)
    unused_in_example = sorted(k for k in example_keys if k not in referenced and k not in SYSTEM_STD_ENVS)

    return {
        "clean": len(missing_in_example) == 0,
        "referenced_count": len(referenced),
        "documented_in_example_count": len(example_keys),
        "missing_from_env_example": [{"var": k, "files": referenced[k][:4]} for k in missing_in_example],
        "undocumented_vars": undocumented_all[:25],
        "unused_in_env_example": unused_in_example[:20],
        "suggested_env_example": "\n".join(f"{k}=" for k in sorted(referenced)),
    }


def render_markdown(rep: Dict[str, Any]) -> str:
    lines = [
        f"### 🔄 Environment & Config Drift Guard (`{rep['referenced_count']}` code vars vs `{rep['documented_in_example_count']}` `.env.example` vars)"
    ]
    if rep["missing_from_env_example"]:
        lines.append("#### ❌ Missing from `.env.example` (Production Crash Risk!)")
        for item in rep["missing_from_env_example"]:
            lines.append(f"- **`{item['var']}`** referenced in `{', '.join(item['files'])}`")
    elif rep["undocumented_vars"]:
        lines.append(f"- ⚠️ No `.env.example` found; discovered `{len(rep['undocumented_vars'])}` env vars: `{', '.join(rep['undocumented_vars'][:10])}`")
    else:
        lines.append("- ✅ **Zero `.env` / code configuration drift!**")
    return "\n".join(lines)


def main() -> int:
    ap = argparse.ArgumentParser(description="Environment & Config Drift Detector")
    ap.add_argument("--workspace", default=".")
    ap.add_argument("--json", action="store_true")
    ns = ap.parse_args()
    rep = audit_env_and_config_drift(Path(ns.workspace))
    print(json.dumps(rep, indent=2, ensure_ascii=False) if ns.json else render_markdown(rep))
    return 0 if rep["clean"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
