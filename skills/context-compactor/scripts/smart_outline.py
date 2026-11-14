#!/usr/bin/env python3
"""AST & Regex Structural File Skeletonizer — Read 2,000-line files in <120 tokens!

Extracts classes, functions, async methods, React components, TypeScript interfaces,
Dart widgets, Go structs/funcs, PHP classes, and Markdown headings WITH exact
`L<start>-L<end>` line numbers so an agent can inspect ONLY the 25 lines it needs!

Also supports `--symbol <name>` to extract the exact code block for one symbol.
Zero external dependencies (Python 3.8+ stdlib only).
"""

from __future__ import annotations

import argparse
import ast
import json
import re
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional


def _configure_utf8() -> None:
    for stream in (sys.stdout, sys.stderr):
        if hasattr(stream, "reconfigure"):
            try:
                stream.reconfigure(encoding="utf-8")
            except Exception:
                pass


PATTERNS_BY_EXT = {
    "ts_js": [
        ("interface/type", re.compile(r"^\s*(?:export\s+)?(?:interface|type|enum)\s+([A-Za-z0-9_$]+)")),
        ("class", re.compile(r"^\s*(?:export\s+)?(?:default\s+)?(?:abstract\s+)?class\s+([A-Za-z0-9_$]+)")),
        ("function", re.compile(r"^\s*(?:export\s+)?(?:default\s+)?(?:async\s+)?function\s+([A-Za-z0-9_$]+)\s*\(")),
        ("const_fn", re.compile(r"^\s*(?:export\s+)?const\s+([A-Za-z0-9_$]+)\s*=\s*(?:async\s*)?(?:\([^)]*\)|[A-Za-z0-9_$]+)\s*=>")),
    ],
    "dart": [
        ("class/widget", re.compile(r"^\s*(?:abstract\s+|sealed\s+|base\s+|final\s+)?(?:class|mixin|enum|extension)\s+([A-Za-z0-9_]+)")),
        ("method", re.compile(r"^\s*(?:@[A-Za-z0-9_]+\s+)?(?:static\s+)?(?:Future<[^>]+>|Stream<[^>]+>|Widget|void|bool|int|double|String|[A-Z][A-Za-z0-9_<>?]*)\s+([a-zA-Z_][A-Za-z0-9_]*)\s*\(")),
    ],
    "go_rs": [
        ("type/struct", re.compile(r"^\s*(?:pub\s+)?(?:type|struct|enum|trait|impl)\s+([A-Za-z0-9_]+)")),
        ("func", re.compile(r"^\s*(?:pub\s+)?(?:async\s+)?(?:func|fn)\s+(?:\([^)]+\)\s*)?([A-Za-z0-9_]+)")),
    ],
    "php": [
        ("class/trait", re.compile(r"^\s*(?:abstract\s+|final\s+)?(?:class|interface|trait)\s+([A-Za-z0-9_]+)")),
        ("function", re.compile(r"^\s*(?:public|protected|private|static|\s)*function\s+([A-Za-z0-9_]+)\s*\(")),
    ],
    "md": [
        ("heading", re.compile(r"^(#{1,3})\s+(.+)$")),
    ],
}


def _outline_python(source: str) -> List[Dict[str, Any]]:
    lines = source.splitlines()
    total = len(lines)
    symbols: List[Dict[str, Any]] = []
    try:
        tree = ast.parse(source)
    except SyntaxError:
        return _outline_regex(lines, [
            ("class", re.compile(r"^\s*class\s+([A-Za-z0-9_]+)")),
            ("def", re.compile(r"^\s*(?:async\s+)?def\s+([A-Za-z0-9_]+)\s*\(")),
        ])

    for node in tree.body:
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            end_ln = getattr(node, "end_lineno", node.lineno)
            args_list = [a.arg for a in node.args.args]
            prefix = "async def" if isinstance(node, ast.AsyncFunctionDef) else "def"
            symbols.append({
                "kind": prefix,
                "name": node.name,
                "signature": f"{prefix} {node.name}({', '.join(args_list[:6])}{'...' if len(args_list) > 6 else ''})",
                "start_line": node.lineno,
                "end_line": end_ln,
            })
        elif isinstance(node, ast.ClassDef):
            end_ln = getattr(node, "end_lineno", node.lineno)
            methods = []
            for child in node.body:
                if isinstance(child, (ast.FunctionDef, ast.AsyncFunctionDef)):
                    m_end = getattr(child, "end_lineno", child.lineno)
                    methods.append({
                        "name": child.name,
                        "start_line": child.lineno,
                        "end_line": m_end,
                    })
            symbols.append({
                "kind": "class",
                "name": node.name,
                "signature": f"class {node.name}",
                "start_line": node.lineno,
                "end_line": end_ln,
                "methods": methods,
            })
    return symbols


def _outline_regex(lines: List[str], rules: List[Any]) -> List[Dict[str, Any]]:
    raw_hits: List[Dict[str, Any]] = []
    for idx, line in enumerate(lines, start=1):
        for kind, regex in rules:
            m = regex.search(line)
            if m:
                if kind == "heading":
                    name = f"{m.group(1)} {m.group(2).strip()}"
                else:
                    name = m.group(1)
                raw_hits.append({
                    "kind": kind,
                    "name": name,
                    "signature": line.strip()[:100],
                    "start_line": idx,
                    "end_line": idx,
                })
                break

    for i, item in enumerate(raw_hits):
        if i + 1 < len(raw_hits):
            item["end_line"] = max(item["start_line"], raw_hits[i + 1]["start_line"] - 1)
        else:
            item["end_line"] = len(lines)
    return raw_hits


def build_outline(fpath: Path) -> Dict[str, Any]:
    source = fpath.read_text(encoding="utf-8", errors="ignore")
    lines = source.splitlines()
    ext = fpath.suffix.lower()

    if ext == ".py":
        symbols = _outline_python(source)
    elif ext in {".ts", ".tsx", ".js", ".jsx", ".mjs", ".cjs"}:
        symbols = _outline_regex(lines, PATTERNS_BY_EXT["ts_js"])
    elif ext == ".dart":
        symbols = _outline_regex(lines, PATTERNS_BY_EXT["dart"])
    elif ext in {".go", ".rs"}:
        symbols = _outline_regex(lines, PATTERNS_BY_EXT["go_rs"])
    elif ext == ".php":
        symbols = _outline_regex(lines, PATTERNS_BY_EXT["php"])
    elif ext in {".md", ".mdx"}:
        symbols = _outline_regex(lines, PATTERNS_BY_EXT["md"])
    else:
        symbols = _outline_regex(lines, PATTERNS_BY_EXT["ts_js"])

    raw_tokens = max(1, int(len(source) / 4))
    return {
        "file": str(fpath).replace("\\", "/"),
        "total_lines": len(lines),
        "full_file_approx_tokens": raw_tokens,
        "symbol_count": len(symbols),
        "symbols": symbols,
    }


def extract_symbol_source(fpath: Path, outline: Dict[str, Any], symbol_query: str) -> Optional[Dict[str, Any]]:
    lines = fpath.read_text(encoding="utf-8", errors="ignore").splitlines()
    q_lower = symbol_query.lower()

    for sym in outline["symbols"]:
        if sym["name"].lower() == q_lower or q_lower in sym["name"].lower():
            s, e = sym["start_line"], sym["end_line"]
            snippet = "\n".join(f"{ln}: {lines[ln - 1]}" for ln in range(s, min(e, len(lines)) + 1))
            return {"symbol": sym["name"], "start_line": s, "end_line": e, "code": snippet}
        for method in sym.get("methods", []):
            full_m = f"{sym['name']}.{method['name']}".lower()
            if method["name"].lower() == q_lower or full_m == q_lower:
                s, e = method["start_line"], method["end_line"]
                snippet = "\n".join(f"{ln}: {lines[ln - 1]}" for ln in range(s, min(e, len(lines)) + 1))
                return {"symbol": f"{sym['name']}.{method['name']}", "start_line": s, "end_line": e, "code": snippet}
    return None


def render_markdown(outline: Dict[str, Any]) -> str:
    lines = [
        f"## Structural Skeleton: `{Path(outline['file']).name}`",
        f"- **Total Lines**: `{outline['total_lines']}` (~`{outline['full_file_approx_tokens']:,}` tokens if read in full)",
        f"- **Extracted Symbols**: `{outline['symbol_count']}` *(use `StartLine`–`EndLine` to read only what you edit)*",
        "",
    ]
    for sym in outline["symbols"]:
        lines.append(f"- **`L{sym['start_line']}-L{sym['end_line']}`** `{sym['signature']}`")
        for m in sym.get("methods", []):
            lines.append(f"  - `L{m['start_line']}-L{m['end_line']}` `.{m['name']}()`")
    outline_text = "\n".join(lines)
    saved_pct = max(0, round((1 - (len(outline_text) / 4) / max(1, outline["full_file_approx_tokens"])) * 100))
    lines.insert(3, f"- **Token Reduction**: **~{saved_pct}% saved** vs full-file read")
    return "\n".join(lines)


def main() -> int:
    _configure_utf8()
    parser = argparse.ArgumentParser(description="Extract compact AST/symbol line-range skeleton from large source files.")
    parser.add_argument("file", help="Path to source file.")
    parser.add_argument("--symbol", "-s", help="Extract exact line-numbered source code for a specific symbol/method.")
    parser.add_argument("--format", choices=("markdown", "json"), default="markdown", help="Output format.")
    args = parser.parse_args()

    fpath = Path(args.file).resolve()
    if not fpath.is_file():
        parser.error(f"File not found: {args.file}")

    outline = build_outline(fpath)
    if args.symbol:
        hit = extract_symbol_source(fpath, outline, args.symbol)
        if not hit:
            print(f"Symbol '{args.symbol}' not found in {fpath.name}. Available symbols:", file=sys.stderr)
            print(render_markdown(outline))
            return 1
        if args.format == "json":
            print(json.dumps(hit, indent=2, ensure_ascii=False))
        else:
            print(f"### `{hit['symbol']}` (`L{hit['start_line']}-L{hit['end_line']}`)\n```\n{hit['code']}\n```")
        return 0

    if args.format == "json":
        print(json.dumps(outline, indent=2, ensure_ascii=False))
    else:
        print(render_markdown(outline))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
