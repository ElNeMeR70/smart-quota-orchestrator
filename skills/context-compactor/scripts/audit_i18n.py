#!/usr/bin/env python3
"""Universal Localization / i18n Drift & Placeholder Auditor (`sqo i18n` / `sqo_i18n_audit`).

Audits Flutter `.arb`, Next.js/React/Vue `locales/*.json` (`messages/*.json`, `i18n/*.json`),
WITHOUT dumping 50,000+ tokens of translated text into the LLM context window!
Outputs an ultra-compact <200-token Delta Matrix:
  1. Missing keys per locale compared to the base union of keys (e.g. `ar` missing 3 keys vs `en`).
  2. Placeholder / Interpolation Mismatches (`{userName}` in `en` vs `{name}` in `ar` — crashes Flutter & next-intl!).
  3. Empty translation values (`""`).

Zero external dependencies (Python 3.8+ stdlib only).
"""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
from pathlib import Path
from typing import Any, Dict, List, Set

IGNORE_DIRS = {".git", "node_modules", ".dart_tool", "build", "dist", ".next", "vendor", "__pycache__", ".sqo"}
PLACEHOLDER_RE = re.compile(r"\{([A-Za-z0-9_]+)\}|\{\{\s*([A-Za-z0-9_]+)\s*\}\}|%(\d+\$)?[sd]")


def _flatten_json(obj: Any, prefix: str = "") -> Dict[str, str]:
    out: Dict[str, str] = {}
    if isinstance(obj, dict):
        for k, v in obj.items():
            if str(k).startswith("@"):
                continue
            full_k = f"{prefix}.{k}" if prefix else str(k)
            if isinstance(v, dict):
                out.update(_flatten_json(v, full_k))
            elif isinstance(v, (str, int, float, bool)):
                out[full_k] = str(v)
    return out


def _extract_placeholders(val: str) -> List[str]:
    found: Set[str] = set()
    for m in PLACEHOLDER_RE.finditer(val):
        tok = m.group(1) or m.group(2) or m.group(0)
        found.add(tok)
    return sorted(found)


def _detect_locale_groups(workspace: Path) -> List[Dict[str, Any]]:
    groups: Dict[str, Dict[str, Path]] = {}
    for root, dirs, files in os.walk(workspace):
        dirs[:] = sorted([d for d in dirs if d not in IGNORE_DIRS])
        rpath = Path(root)
        for fn in sorted(files):
            fpath = rpath / fn
            ext = fpath.suffix.lower()
            if ext == ".arb":
                m = re.match(r"^(?:app_|intl_)?([a-z]{2}(?:_[A-Z]{2})?)\.arb$", fn)
                loc = m.group(1) if m else fpath.stem
                groups.setdefault(rpath.relative_to(workspace).as_posix(), {})[loc] = fpath
            elif ext == ".json" and any(seg in {"locales", "locale", "messages", "i18n", "translations", "lang"} for seg in fpath.parts):
                loc = fpath.stem
                if re.match(r"^[a-z]{2}(?:[-_][A-Za-z]{2,4})?$", loc):
                    groups.setdefault(rpath.relative_to(workspace).as_posix(), {})[loc] = fpath

    return [{"dir": d, "locales": locs} for d, locs in groups.items() if len(locs) >= 2]


def audit_workspace_i18n(workspace: Path) -> Dict[str, Any]:
    ws = workspace.resolve()
    groups = _detect_locale_groups(ws)
    raw_bytes = 0
    group_reports: List[Dict[str, Any]] = []
    total_missing = 0
    total_placeholder_bugs = 0

    for grp in groups:
        loc_maps: Dict[str, Dict[str, str]] = {}
        for loc, fpath in sorted(grp["locales"].items()):
            try:
                raw = fpath.read_text(encoding="utf-8", errors="ignore")
                raw_bytes += len(raw.encode("utf-8", errors="ignore"))
                loc_maps[loc] = _flatten_json(json.loads(raw))
            except Exception:
                continue
        if len(loc_maps) < 2:
            continue

        all_keys: Set[str] = set()
        for kv in loc_maps.values():
            all_keys.update(kv.keys())

        base_loc = "en" if "en" in loc_maps else sorted(loc_maps.keys())[0]
        missing_by_locale: Dict[str, List[str]] = {}
        empty_by_locale: Dict[str, List[str]] = {}
        placeholder_mismatches: List[Dict[str, Any]] = []

        for loc, kv in sorted(loc_maps.items()):
            miss = sorted(all_keys - set(kv.keys()))
            if miss:
                missing_by_locale[loc] = miss
                total_missing += len(miss)
            empties = sorted([k for k, v in kv.items() if not v.strip()])
            if empties:
                empty_by_locale[loc] = empties

        base_kv = loc_maps[base_loc]
        for k in sorted(all_keys):
            if k not in base_kv:
                continue
            base_ph = _extract_placeholders(base_kv[k])
            for loc, kv in sorted(loc_maps.items()):
                if loc == base_loc or k not in kv:
                    continue
                cur_ph = _extract_placeholders(kv[k])
                if cur_ph != base_ph:
                    total_placeholder_bugs += 1
                    placeholder_mismatches.append(
                        {"key": k, "base_locale": base_loc, "base_vars": base_ph, "locale": loc, "locale_vars": cur_ph}
                    )

        group_reports.append(
            {
                "directory": grp["dir"],
                "locales": sorted(loc_maps.keys()),
                "total_unique_keys": len(all_keys),
                "missing_by_locale": missing_by_locale,
                "empty_by_locale": empty_by_locale,
                "placeholder_mismatches": placeholder_mismatches[:25],
            }
        )

    raw_tokens = max(1, int(raw_bytes / 4)) if raw_bytes else 0
    summary_json = json.dumps(group_reports, ensure_ascii=False)
    compact_tokens = max(1, int(len(summary_json) / 4)) if group_reports else 0
    savings_pct = round(max(0.0, (1.0 - compact_tokens / raw_tokens) * 100.0), 1) if raw_tokens else 0.0

    return {
        "i18n_groups_found": len(group_reports),
        "healthy": total_missing == 0 and total_placeholder_bugs == 0,
        "total_missing_keys": total_missing,
        "total_placeholder_mismatches": total_placeholder_bugs,
        "raw_locale_tokens": raw_tokens,
        "delta_report_tokens": compact_tokens,
        "token_savings_pct": savings_pct,
        "groups": group_reports,
    }


def render_markdown(rep: Dict[str, Any]) -> str:
    if rep["i18n_groups_found"] == 0:
        return "## 🌐 i18n Drift Auditor\n_No multi-locale `.arb` or `locales/*.json` bundles found in workspace._"
    status = "✅ 100% IN SYNC" if rep["healthy"] else f"⚠️ {rep['total_missing_keys']} Missing Keys & {rep['total_placeholder_mismatches']} Placeholder Bugs"
    lines = [
        f"## 🌐 i18n Localization Delta Matrix — {status} (`-{rep['token_savings_pct']}%` Token Savings)",
        f"- **Raw Locale Files**: `~{rep['raw_locale_tokens']:,}` tok -> **Compact Delta**: `~{rep['delta_report_tokens']:,}` tok",
    ]
    for g in rep["groups"]:
        lines.append(f"\n### 📂 `{g['directory']}` (`{len(g['locales'])}` locales: `{', '.join(g['locales'])}` | `{g['total_unique_keys']}` keys)")
        for loc, miss in g["missing_by_locale"].items():
            lines.append(f"- ❌ **`{loc}` missing `{len(miss)}` key(s)**: `{', '.join(miss[:12])}`")
        for pm in g["placeholder_mismatches"]:
            lines.append(f"- 🚨 **Placeholder Bug in `{pm['key']}`**: `{pm['base_locale']}` has `{pm['base_vars']}` vs `{pm['locale']}` has `{pm['locale_vars']}`")
    return "\n".join(lines)


def main() -> int:
    for s in (sys.stdout, sys.stderr):
        if hasattr(s, "reconfigure"):
            try:
                s.reconfigure(encoding="utf-8")
            except Exception:
                pass
    parser = argparse.ArgumentParser(description="Universal Flutter .arb & JSON Localization Drift Auditor.")
    parser.add_argument("--workspace", "-w", default=".", help="Workspace root.")
    parser.add_argument("--format", choices=("markdown", "json"), default="markdown")
    args = parser.parse_args()

    rep = audit_workspace_i18n(Path(args.workspace))
    if args.format == "json":
        print(json.dumps(rep, indent=2, ensure_ascii=False))
    else:
        print(render_markdown(rep))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
