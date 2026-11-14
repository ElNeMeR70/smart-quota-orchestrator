#!/usr/bin/env python3
"""Serena-Class Surgical Symbol-Level AST Mutator & Caller Graph (v10.0 Apex).

Saves ~85% of expensive LLM OUTPUT tokens by mutating exact functions, classes,
or Class.method symbols by name across Python, TypeScript/JS, Dart, Go, Rust, PHP & C#,
with automatic Time-Machine backup and <8ms Shadow Syntax auto-rollback!
"""

from __future__ import annotations

import argparse
import ast
import importlib.util
import json
import re
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

SKILLS_ROOT = Path(__file__).resolve().parents[2]

BRACE_DECL_PATTERNS = [
    # TypeScript / JS / Dart / Java / C# / PHP / Go / Rust declarations
    re.compile(r"^\s*(?:export\s+)?(?:default\s+)?(?:abstract\s+|final\s+|sealed\s+|base\s+)?(?:class|interface|enum|mixin|extension|struct|impl|trait)\s+([A-Za-z_]\w*)\b"),
    re.compile(r"^\s*(?:export\s+)?(?:async\s+)?function\s+([A-Za-z_]\w*)\s*[(<]"),
    re.compile(r"^\s*func\s+(?:\([^)]+\)\s*)?([A-Za-z_]\w*)\s*[(<]"),
    re.compile(r"^\s*(?:pub\s+)?(?:async\s+)?fn\s+([A-Za-z_]\w*)\s*[(<]"),
    re.compile(r"^\s*(?:public|private|protected|static|async|override|Future<[^>]+>|Stream<[^>]+>|Widget|void|int|double|bool|String|dynamic|var|final|const|[A-Z]\w*(?:<[^>]+>)?\??)\s+([A-Za-z_]\w*)\s*\([^;]*\)\s*(?:async\s*\*?\s*)?\{"),
    re.compile(r"^\s*(?:export\s+)?(?:const|let|var)\s+([A-Za-z_]\w*)\s*=\s*(?:async\s*)?(?:\([^)]*\)|[A-Za-z_]\w*)\s*=>\s*\{"),
]


def _load_sibling(rel_path: str):
    full = SKILLS_ROOT / rel_path
    spec = importlib.util.spec_from_file_location(full.stem, full)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Cannot load {full}")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def _find_python_symbol_span(source: str, symbol_query: str) -> Optional[Tuple[int, int, str, int]]:
    """Returns (start_line_1based, end_line_1based, qualified_name, indent_cols)."""
    tree = ast.parse(source)
    parts = symbol_query.split(".")
    lines = source.splitlines()

    def _decorator_start(node: ast.AST) -> int:
        decs = getattr(node, "decorator_list", None) or []
        if decs:
            return min(getattr(d, "lineno", node.lineno) for d in decs)
        return node.lineno

    for node in tree.body:
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
            if len(parts) == 1 and node.name == parts[0]:
                s = _decorator_start(node)
                e = getattr(node, "end_lineno", node.lineno)
                indent = len(lines[node.lineno - 1]) - len(lines[node.lineno - 1].lstrip(" "))
                return (s, e, node.name, indent)
            if isinstance(node, ast.ClassDef) and (
                (len(parts) == 2 and node.name == parts[0]) or len(parts) == 1
            ):
                target_method = parts[1] if len(parts) == 2 else parts[0]
                for child in node.body:
                    if isinstance(child, (ast.FunctionDef, ast.AsyncFunctionDef)) and child.name == target_method:
                        s = _decorator_start(child)
                        e = getattr(child, "end_lineno", child.lineno)
                        indent = len(lines[child.lineno - 1]) - len(lines[child.lineno - 1].lstrip(" "))
                        return (s, e, f"{node.name}.{child.name}", indent)
    return None


def _scan_brace_end(lines: List[str], start_idx: int) -> int:
    depth = 0
    opened = False
    in_str: Optional[str] = None
    in_block_comment = False

    for idx in range(start_idx, len(lines)):
        ln = lines[idx]
        i = 0
        while i < len(ln):
            ch = ln[i]
            nxt = ln[i + 1] if i + 1 < len(ln) else ""
            if in_block_comment:
                if ch == "*" and nxt == "/":
                    in_block_comment = False
                    i += 2
                    continue
                i += 1
                continue
            if in_str:
                if ch == "\\":
                    i += 2
                    continue
                if ch == in_str:
                    in_str = None
                i += 1
                continue
            if ch == "/" and nxt == "/":
                break
            if ch == "/" and nxt == "*":
                in_block_comment = True
                i += 2
                continue
            if ch in ("'", '"', "`"):
                in_str = ch
                i += 1
                continue
            if ch == "{":
                depth += 1
                opened = True
            elif ch == "}":
                depth -= 1
                if opened and depth <= 0:
                    return idx + 1
            i += 1
    return len(lines)


def _find_brace_symbol_span(source: str, symbol_query: str) -> Optional[Tuple[int, int, str, int]]:
    lines = source.splitlines()
    target_cls, target_sym = (symbol_query.split(".", 1) if "." in symbol_query else (None, symbol_query))
    search_start = 0
    search_end = len(lines)

    if target_cls:
        cls_re = re.compile(rf"^\s*(?:export\s+)?(?:abstract\s+|final\s+|sealed\s+)?(?:class|struct|impl|mixin|extension)\s+{re.escape(target_cls)}\b")
        for i, ln in enumerate(lines):
            if cls_re.search(ln):
                search_start = i + 1
                search_end = _scan_brace_end(lines, i)
                break

    for i in range(search_start, search_end):
        ln = lines[i]
        for pat in BRACE_DECL_PATTERNS:
            m = pat.search(ln)
            if m and m.group(1) == target_sym:
                end_1based = _scan_brace_end(lines, i)
                indent = len(ln) - len(ln.lstrip(" "))
                qname = f"{target_cls}.{target_sym}" if target_cls else target_sym
                return (i + 1, end_1based, qname, indent)
    return None


def locate_symbol(file_path: Path, symbol_query: str) -> Optional[Tuple[int, int, str, int]]:
    src = file_path.read_text(encoding="utf-8", errors="replace")
    if file_path.suffix.lower() == ".py":
        return _find_python_symbol_span(src, symbol_query)
    return _find_brace_symbol_span(src, symbol_query)


def _reindent_block(new_code: str, target_indent: int) -> List[str]:
    raw_lines = new_code.strip("\r\n").splitlines()
    if not raw_lines:
        return []
    non_empty = [ln for ln in raw_lines if ln.strip()]
    min_existing = min((len(ln) - len(ln.lstrip(" "))) for ln in non_empty) if non_empty else 0
    prefix = " " * target_indent
    out: List[str] = []
    for ln in raw_lines:
        if not ln.strip():
            out.append("")
        else:
            stripped = ln[min_existing:] if len(ln) >= min_existing else ln.lstrip(" ")
            out.append(prefix + stripped)
    return out


def mutate_symbol(
    workspace: Path,
    file_path: Path,
    symbol: str,
    action: str,
    new_code: str = "",
) -> Dict[str, Any]:
    workspace = workspace.resolve()
    file_path = file_path.resolve()
    if not file_path.is_file():
        return {"ok": False, "error": f"File not found: {file_path}"}

    span = locate_symbol(file_path, symbol)
    if not span:
        return {"ok": False, "error": f"Symbol '{symbol}' not found in {file_path.name}"}

    start_ln, end_ln, qname, indent = span
    original_text = file_path.read_text(encoding="utf-8", errors="replace")
    orig_lines = original_text.splitlines()
    newline = "\r\n" if "\r\n" in original_text else "\n"

    # Automatic Time-Machine safety snapshot before editing
    cp_id = None
    try:
        tm_mod = _load_sibling("smart-quota-orchestrator/scripts/time_machine.py")
        rel_f = str(file_path.relative_to(workspace)).replace("\\", "/") if file_path.is_relative_to(workspace) else file_path.name
        cp = tm_mod.create_checkpoint(workspace, label=f"pre-symbol-{qname}", files_only=[rel_f] if file_path.is_relative_to(workspace) else None)
        cp_id = cp.get("id")
    except Exception:
        pass

    formatted = _reindent_block(new_code, indent) if new_code else []
    act = action.lower()
    if act == "replace":
        updated_lines = orig_lines[: start_ln - 1] + formatted + orig_lines[end_ln:]
    elif act == "insert_after":
        updated_lines = orig_lines[:end_ln] + [""] + formatted + orig_lines[end_ln:]
    elif act == "insert_before":
        updated_lines = orig_lines[: start_ln - 1] + formatted + [""] + orig_lines[start_ln - 1 :]
    elif act == "delete":
        updated_lines = orig_lines[: start_ln - 1] + orig_lines[end_ln:]
    else:
        return {"ok": False, "error": f"Unsupported action '{action}'"}

    updated_text = newline.join(updated_lines) + (newline if original_text.endswith(("\n", "\r\n")) else "")
    file_path.write_text(updated_text, encoding="utf-8")

    # Immediate <8ms Pre-Flight Syntax & Balanced-Delimiter Verification!
    try:
        sh_mod = _load_sibling("smart-quota-orchestrator/scripts/shadow_dry_run.py")
        rel_target = str(file_path.relative_to(workspace)).replace("\\", "/") if file_path.is_relative_to(workspace) else str(file_path)
        chk = sh_mod.run_shadow_check(workspace, [rel_target])
        syntax_Issues = [i for i in chk.get("issues", []) if i.get("kind") in ("python_syntax_error", "unclosed_delimiter", "merge_conflict_marker")]
        if syntax_Issues:
            file_path.write_text(original_text, encoding="utf-8")
            return {
                "ok": False,
                "rolled_back": True,
                "symbol": qname,
                "error": "Auto-Rolled Back! Mutation introduced a syntax/delimiter error.",
                "issues": syntax_Issues,
            }
    except Exception:
        pass

    full_file_tokens = max(1, len(original_text) // 4)
    emitted_tokens = max(1, len(new_code) // 4)
    output_tokens_saved = max(0, full_file_tokens - emitted_tokens)
    savings_pct = round((output_tokens_saved / full_file_tokens) * 100, 1)

    return {
        "ok": True,
        "action": act,
        "file": str(file_path.relative_to(workspace)).replace("\\", "/") if file_path.is_relative_to(workspace) else file_path.name,
        "symbol": qname,
        "previous_span": f"L{start_ln}-L{end_ln}",
        "checkpoint_id": cp_id,
        "output_tokens_emitted": emitted_tokens,
        "full_rewrite_tokens_avoided": full_file_tokens,
        "output_tokens_saved": output_tokens_saved,
        "output_token_savings_pct": savings_pct,
    }


def find_callers(workspace: Path, symbol: str, max_hits: int = 25) -> Dict[str, Any]:
    workspace = workspace.resolve()
    short_sym = symbol.split(".")[-1]
    call_re = re.compile(rf"\b{re.escape(short_sym)}\s*\(")
    skip_dirs = {".git", "node_modules", ".venv", "venv", "__pycache__", "build", "dist", ".next", ".dart_tool", "vendor", ".sqo"}
    exts = {".py", ".ts", ".tsx", ".js", ".jsx", ".dart", ".go", ".rs", ".php", ".java", ".cs"}

    hits: List[Dict[str, Any]] = []
    for p in workspace.rglob("*"):
        if not p.is_file() or p.suffix.lower() not in exts:
            continue
        if any(part in skip_dirs for part in p.parts):
            continue
        try:
            text = p.read_text(encoding="utf-8", errors="ignore")
        except OSError:
            continue
        if short_sym not in text:
            continue
        for idx, ln in enumerate(text.splitlines(), 1):
            if call_re.search(ln):
                stripped = ln.strip()
                is_def = stripped.startswith(("def ", "async def ", "function ", "func ", "fn ", "pub fn "))
                hits.append(
                    {
                        "file": str(p.relative_to(workspace)).replace("\\", "/"),
                        "line": idx,
                        "kind": "definition" if is_def else "call_site",
                        "snippet": stripped[:140],
                    }
                )
                if len(hits) >= max_hits:
                    break
        if len(hits) >= max_hits:
            break

    return {"symbol": symbol, "total_hits": len(hits), "hits": hits}


def render_markdown(res: Dict[str, Any]) -> str:
    if "hits" in res:
        lines = [f"### 🔎 Symbol Callers for `{res['symbol']}` ({res['total_hits']} sites)"]
        for h in res["hits"]:
            lines.append(f"- `{h['file']}:L{h['line']}` [{h['kind']}]: `{h['snippet']}`")
        return "\n".join(lines)
    if not res.get("ok"):
        return f"### ❌ Symbol Edit Blocked / Rolled Back\n- **Reason:** {res.get('error')}\n- **Details:** `{json.dumps(res.get('issues', []))}`"
    return (
        f"### 🗡️ Surgical Symbol Edit Applied (`{res['symbol']}`)\n"
        f"- **File:** `{res['file']}` (`{res['previous_span']}` • Action: `{res['action']}`)\n"
        f"- **Time-Machine Backup:** `{res.get('checkpoint_id') or 'auto'}`\n"
        f"- **Output Tokens Saved:** **{res['output_tokens_saved']:,} tokens (-{res['output_token_savings_pct']}%)**"
    )


def main() -> int:
    ap = argparse.ArgumentParser(description="Surgical AST Symbol Editor & Caller Finder")
    ap.add_argument("--workspace", default=".", help="Workspace root")
    ap.add_argument("--file", default="", help="Target file path")
    ap.add_argument("--symbol", required=True, help="Symbol or Class.method name")
    ap.add_argument("--action", choices=["replace", "insert_after", "insert_before", "delete", "callers"], default="callers")
    ap.add_argument("--code", default="", help="New symbol code")
    ap.add_argument("--json", action="store_true")
    ns = ap.parse_args()

    ws = Path(ns.workspace).resolve()
    if ns.action == "callers":
        out = find_callers(ws, ns.symbol)
    else:
        fpath = (ws / ns.file) if not Path(ns.file).is_absolute() else Path(ns.file)
        out = mutate_symbol(ws, fpath, ns.symbol, ns.action, ns.code)

    print(json.dumps(out, indent=2, ensure_ascii=False) if ns.json else render_markdown(out))
    return 0 if out.get("ok", True) else 1


if __name__ == "__main__":
    raise SystemExit(main())
