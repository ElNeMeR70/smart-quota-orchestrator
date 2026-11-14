#!/usr/bin/env python3
"""Always-On Rules & Skill Frontmatter Token-Tax Profiler.

Audits `AGENTS.md`, `CLAUDE.md`, `GEMINI.md`, `.cursorrules`, `.windsurfrules`,
`.github/copilot-instructions.md`, and `skills/**/SKILL.md` to calculate:
  - Always-On Context Tax (tokens billed on EVERY turn unconditionally!)
  - Progressive-Disclosure Index Tax (skill name + description tokens)
  - Bloated instruction files that should offload examples into `references/`
  - Missing frontmatter fields or overly vague skill descriptions

Zero external dependencies (Python 3.8+ stdlib only).
"""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
from pathlib import Path
from typing import Any, Dict, List

ALWAYS_ON_FILENAMES = {
    "agents.md",
    "claude.md",
    "gemini.md",
    ".cursorrules",
    ".windsurfrules",
    "copilot-instructions.md",
}

IGNORE_DIRS = {".git", "node_modules", ".next", "dist", "build", "__pycache__", ".venv", "venv"}


def _configure_utf8() -> None:
    for stream in (sys.stdout, sys.stderr):
        if hasattr(stream, "reconfigure"):
            try:
                stream.reconfigure(encoding="utf-8")
            except Exception:
                pass


def _parse_frontmatter(text: str) -> Dict[str, str]:
    m = re.match(r"^---\s*\n(.*?)\n---\s*\n", text, flags=re.DOTALL)
    if not m:
        return {}
    block = m.group(1)
    out: Dict[str, str] = {}
    name_m = re.search(r"^name:\s*(.+)$", block, flags=re.MULTILINE)
    if name_m:
        out["name"] = name_m.group(1).strip().strip("'\"")
    desc_m = re.search(r"^description:\s*(?:>-\s*\n((?:  .+\n?)+)|(.+))$", block, flags=re.MULTILINE)
    if desc_m:
        raw_desc = desc_m.group(1) or desc_m.group(2) or ""
        out["description"] = " ".join(ln.strip() for ln in raw_desc.splitlines()).strip("'\"")
    return out


def profile_workspace(workspace: Path, turns_per_session: int = 25) -> Dict[str, Any]:
    always_on_files: List[Dict[str, Any]] = []
    skill_files: List[Dict[str, Any]] = []
    warnings: List[str] = []

    for dirpath, dirnames, filenames in os.walk(workspace):
        dirnames[:] = [d for d in dirnames if d not in IGNORE_DIRS]
        for fname in filenames:
            fpath = Path(dirpath) / fname
            rel = str(fpath.relative_to(workspace)).replace("\\", "/")
            fl = fname.lower()

            if fl in ALWAYS_ON_FILENAMES or rel.startswith((".agents/rules/", ".cursor/rules/")):
                text = fpath.read_text(encoding="utf-8", errors="ignore")
                tok = max(1, int(len(text) / 4))
                code_blocks = len(re.findall(r"```", text)) // 2
                always_on_files.append({
                    "file": rel,
                    "lines": len(text.splitlines()),
                    "approx_tokens": tok,
                    "embedded_code_blocks": code_blocks,
                })
                if tok > 1200:
                    warnings.append(
                        f"`{rel}` costs ~{tok:,} tokens on EVERY turn (~{tok * turns_per_session:,} tokens over {turns_per_session} turns). Move bulky code examples into an on-demand skill or `references/` doc."
                    )
            elif fname == "SKILL.md":
                text = fpath.read_text(encoding="utf-8", errors="ignore")
                fm = _parse_frontmatter(text)
                body_tok = max(1, int(len(text) / 4))
                index_tok = max(1, int((len(fm.get("name", "")) + len(fm.get("description", ""))) / 4))
                skill_files.append({
                    "file": rel,
                    "name": fm.get("name", "(missing)"),
                    "index_tokens": index_tok,
                    "full_skill_tokens": body_tok,
                    "has_valid_frontmatter": bool(fm.get("name") and fm.get("description")),
                })
                if not (fm.get("name") and fm.get("description")):
                    warnings.append(f"`{rel}` is missing required `name` or `description` YAML frontmatter.")
                elif len(fm.get("description", "")) < 40:
                    warnings.append(f"`{rel}` has a very short `description` — specify clear trigger conditions ('Use when...') so agents activate it accurately.")
                if body_tok > 2500:
                    warnings.append(f"`{rel}` is ~{body_tok:,} tokens — split deep manuals into `references/*.md` for progressive disclosure.")

    always_on_tax = sum(x["approx_tokens"] for x in always_on_files)
    skill_index_tax = sum(x["index_tokens"] for x in skill_files)
    per_turn_baseline = always_on_tax + skill_index_tax
    session_overhead = per_turn_baseline * turns_per_session

    if per_turn_baseline <= 800:
        grade = "A+ (Ultra-Lean Prompt Architecture)"
    elif per_turn_baseline <= 2000:
        grade = "B (Healthy Static Context)"
    else:
        grade = "C/D (Heavy Always-On Tax — Refactor to Progressive Disclosure)"

    return {
        "workspace": str(workspace).replace("\\", "/"),
        "grade": grade,
        "always_on_tokens_per_turn": always_on_tax,
        "skill_index_tokens_per_turn": skill_index_tax,
        "total_baseline_tokens_per_turn": per_turn_baseline,
        "projected_overhead_25_turns": session_overhead,
        "always_on_files": sorted(always_on_files, key=lambda x: -x["approx_tokens"]),
        "skills": sorted(skill_files, key=lambda x: -x["full_skill_tokens"]),
        "optimization_warnings": warnings,
    }


def render_markdown(rep: Dict[str, Any]) -> str:
    lines = [
        "## Prompt & Customization Token-Tax Profile",
        "",
        "| Metric | Value |",
        "| :--- | :--- |",
        f"| **Architecture Grade** | **{rep['grade']}** |",
        f"| **Always-On Rule Tax / Turn** | `~{rep['always_on_tokens_per_turn']:,}` tokens (`{len(rep['always_on_files'])}` file(s)) |",
        f"| **Skill Discovery Index / Turn** | `~{rep['skill_index_tokens_per_turn']:,}` tokens (`{len(rep['skills'])}` skill(s)) |",
        f"| **Total Static Tax (25-Turn Session)** | **`~{rep['projected_overhead_25_turns']:,}` tokens** |",
    ]
    if rep["always_on_files"]:
        lines.extend(["", "### Always-On Rule Files", ""])
        for f in rep["always_on_files"]:
            lines.append(f"- `{f['file']}` — `~{f['approx_tokens']:,}` tokens (`{f['lines']}` lines, `{f['embedded_code_blocks']}` code block(s))")
    if rep["skills"]:
        lines.extend(["", "### On-Demand Skills (Progressive Disclosure)", ""])
        for s in rep["skills"]:
            lines.append(
                f"- **{s['name']}** (`{s['file']}`) — Index cost: `~{s['index_tokens']}` tok/turn | On-activation body: `~{s['full_skill_tokens']:,}` tok"
            )
    if rep["optimization_warnings"]:
        lines.extend(["", "### Optimization Recommendations", ""])
        for w in rep["optimization_warnings"]:
            lines.append(f"- {w}")
    else:
        lines.extend(["", "### Optimization Recommendations", "", "- Zero prompt-bloat issues detected! Rules and skills follow progressive disclosure cleanly."])
    return "\n".join(lines)


def main() -> int:
    _configure_utf8()
    parser = argparse.ArgumentParser(description="Profile static token tax of AGENTS.md, CLAUDE.md, GEMINI.md, and SKILL.md files.")
    parser.add_argument("--workspace", "-w", default=".", help="Workspace directory to scan.")
    parser.add_argument("--turns", "-t", type=int, default=25, help="Turns per session to model (default: 25).")
    parser.add_argument("--format", choices=("markdown", "json"), default="markdown", help="Output format.")
    args = parser.parse_args()

    rep = profile_workspace(Path(args.workspace).resolve(), turns_per_session=args.turns)
    if args.format == "json":
        print(json.dumps(rep, indent=2, ensure_ascii=False))
    else:
        print(render_markdown(rep))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
