#!/usr/bin/env python3
"""Multi-Modal Vision & PDF Token Cost Estimator (`sqo media`).

Reads PNG, JPEG, WebP, GIF dimensions and PDF page counts using 100% pure Python
stdlib (`struct` + binary headers — zero Pillow or PyPDF dependencies!) and calculates
exact vision/document input token costs across Gemini, Claude, and OpenAI models,
flagging oversized 4K screenshots that waste quota!
"""

from __future__ import annotations

import argparse
import json
import math
import os
import re
import struct
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

MEDIA_EXTS = {".png", ".jpg", ".jpeg", ".webp", ".gif", ".pdf"}
IGNORE_DIRS = {".git", ".sqo", "node_modules", ".next", "dist", "build", "__pycache__", ".venv", "venv"}


def _configure_utf8() -> None:
    for stream in (sys.stdout, sys.stderr):
        if hasattr(stream, "reconfigure"):
            try:
                stream.reconfigure(encoding="utf-8")
            except Exception:
                pass


def parse_image_dimensions(fpath: Path) -> Optional[Tuple[int, int]]:
    try:
        with open(fpath, "rb") as fh:
            head = fh.read(64)
            if len(head) < 16:
                return None

            # PNG: 8-byte signature + IHDR chunk (width, height big-endian uint32 at offset 16..24)
            if head[:8] == b"\x89PNG\r\n\x1a\n" and len(head) >= 24:
                w, h = struct.unpack(">II", head[16:24])
                return int(w), int(h)

            # GIF87a / GIF89a: little-endian uint16 at offset 6..10
            if head[:6] in (b"GIF87a", b"GIF89a"):
                w, h = struct.unpack("<HH", head[6:10])
                return int(w), int(h)

            # WebP (VP8 / VP8L / VP8X)
            if head[:4] == b"RIFF" and head[8:12] == b"WEBP" and len(head) >= 30:
                chunk = head[12:16]
                if chunk == b"VP8X":
                    w = 1 + int.from_bytes(head[24:27], "little")
                    h = 1 + int.from_bytes(head[27:30], "little")
                    return w, h
                if chunk == b"VP8L":
                    bits = struct.unpack("<I", head[21:25])[0]
                    w = (bits & 0x3FFF) + 1
                    h = ((bits >> 14) & 0x3FFF) + 1
                    return w, h
                if chunk == b"VP8 ":
                    w, h = struct.unpack("<HH", head[26:30])
                    return int(w & 0x3FFF), int(h & 0x3FFF)

            # JPEG: scan SOF0..SOF3 / SOF5..SOF15 markers
            if head[:2] == b"\xff\xd8":
                fh.seek(2)
                while True:
                    b = fh.read(1)
                    if not b:
                        break
                    if b != b"\xff":
                        continue
                    while b == b"\xff":
                        b = fh.read(1)
                    if not b:
                        break
                    marker = b[0]
                    if marker in (0xD8, 0xD9) or (0xD0 <= marker <= 0xD7):
                        continue
                    seg_len_bytes = fh.read(2)
                    if len(seg_len_bytes) < 2:
                        break
                    seg_len = struct.unpack(">H", seg_len_bytes)[0]
                    if marker in (0xC0, 0xC1, 0xC2, 0xC3, 0xC5, 0xC6, 0xC7, 0xC9, 0xCA, 0xCB, 0xCD, 0xCE, 0xCF):
                        sof = fh.read(5)
                        if len(sof) == 5:
                            _, h, w = struct.unpack(">BHH", sof)
                            return int(w), int(h)
                        break
                    fh.seek(max(0, seg_len - 2), os.SEEK_CUR)
    except OSError:
        return None
    return None


def estimate_pdf_pages(fpath: Path) -> int:
    try:
        raw = fpath.read_bytes()
        counts = [int(m.group(1)) for m in re.finditer(rb"/Count\s+(\d+)", raw)]
        if counts:
            return max(counts)
        pages = len(re.findall(rb"/Type\s*/Page\b", raw))
        return max(1, pages)
    except OSError:
        return 1


def estimate_file_media_tokens(fpath: Path) -> Dict[str, Any]:
    ext = fpath.suffix.lower()
    size_kb = round(fpath.stat().st_size / 1024.0, 1) if fpath.is_file() else 0.0

    if ext == ".pdf":
        pages = estimate_pdf_pages(fpath)
        # Gemini bills ~258 vision tokens/page + extracted text; Claude bills ~1,500-2,200 tok/page
        gemini_tok = pages * 258
        claude_tok = pages * 1650
        openai_tok = pages * 1100
        advice = "Pass explicit `StartLine`/`EndLine` or page ranges instead of reading entire multi-page PDFs." if pages > 10 else "Optimal size."
        return {
            "file": str(fpath).replace("\\", "/"),
            "type": "pdf",
            "size_kb": size_kb,
            "dimensions_or_pages": f"{pages} page(s)",
            "gemini_tokens": gemini_tok,
            "claude_tokens": claude_tok,
            "openai_tokens": openai_tok,
            "oversized": pages > 12,
            "recommendation": advice,
        }

    dims = parse_image_dimensions(fpath)
    if dims is None:
        w, h = 1024, 1024
        dim_label = "unknown (est. 1024x1024)"
    else:
        w, h = dims
        dim_label = f"{w}x{h}"

    # Gemini tiling: <=384px both sides = 258 tokens; larger tiled into 768x768 @ 258 tok/tile
    if w <= 384 and h <= 384:
        gemini_tiles = 1
    else:
        gemini_tiles = max(1, math.ceil(w / 768.0) * math.ceil(h / 768.0))
    gemini_tok = gemini_tiles * 258

    # Anthropic formula: ~(width * height) / 750 (clamped to <=1568px long edge internally, still heavy at 2K+)
    scale = min(1.0, 1568.0 / max(w, h, 1))
    cw, ch = int(w * scale), int(h * scale)
    claude_tok = max(85, int((cw * ch) / 750.0))

    # OpenAI high-detail tiling: scale shortest side to 768, 512x512 tiles * 170 + 85
    o_tiles = max(1, math.ceil(min(w, 2048) / 512.0) * math.ceil(min(h, 2048) / 512.0))
    openai_tok = 85 + o_tiles * 170

    oversized = max(w, h) > 1600 or size_kb > 1500
    advice = (
        f"Downscale to <=1280px max edge to cut vision tokens by ~{max(35, int((1 - 258 / max(gemini_tok, 259)) * 100))}%!"
        if oversized
        else "Optimal resolution for multimodal context."
    )

    return {
        "file": str(fpath).replace("\\", "/"),
        "type": "image",
        "size_kb": size_kb,
        "dimensions_or_pages": dim_label,
        "gemini_tokens": gemini_tok,
        "claude_tokens": claude_tok,
        "openai_tokens": openai_tok,
        "oversized": oversized,
        "recommendation": advice,
    }


def scan_media_paths(targets: List[str], workspace: Path) -> Dict[str, Any]:
    files: List[Path] = []
    if targets:
        for t in targets:
            p = Path(t) if Path(t).is_absolute() else (workspace / t)
            if p.is_file() and p.suffix.lower() in MEDIA_EXTS:
                files.append(p.resolve())
            elif p.is_dir():
                for dp, dns, fns in os.walk(p):
                    dns[:] = [d for d in dns if d not in IGNORE_DIRS]
                    for fn in fns:
                        fp = Path(dp) / fn
                        if fp.suffix.lower() in MEDIA_EXTS:
                            files.append(fp.resolve())
    else:
        for dp, dns, fns in os.walk(workspace):
            dns[:] = [d for d in dns if d not in IGNORE_DIRS]
            for fn in fns:
                fp = Path(dp) / fn
                if fp.suffix.lower() in MEDIA_EXTS:
                    files.append(fp.resolve())

    files = sorted(set(files))[:60]
    items = [estimate_file_media_tokens(f) for f in files]
    return {
        "scanned_count": len(items),
        "total_gemini_tokens": sum(x["gemini_tokens"] for x in items),
        "total_claude_tokens": sum(x["claude_tokens"] for x in items),
        "total_openai_tokens": sum(x["openai_tokens"] for x in items),
        "oversized_count": sum(1 for x in items if x["oversized"]),
        "items": items,
    }


def render_markdown(rep: Dict[str, Any]) -> str:
    lines = [
        "## 🖼️ Multi-Modal Vision & PDF Token Cost Audit",
        f"- **Media Assets Scanned**: `{rep['scanned_count']}` (`{rep['oversized_count']}` oversized 4K/multi-page asset(s))",
        f"- **Total Token Cost If Loaded**: Gemini: **`{rep['total_gemini_tokens']:,}`** | Claude: **`{rep['total_claude_tokens']:,}`** | OpenAI: **`{rep['total_openai_tokens']:,}`**",
        "",
    ]
    if not rep["items"]:
        lines.append("_No PNG/JPEG/WebP/GIF/PDF media files found in target scope._")
        return "\n".join(lines)

    lines.extend([
        "| Asset | Specs | Size | Gemini Tok | Claude Tok | OpenAI Tok | Advice |",
        "| :--- | :--- | :--- | :--- | :--- | :--- | :--- |",
    ])
    for it in rep["items"]:
        short_name = Path(it["file"]).name
        flag = "⚠️ " if it["oversized"] else "✅ "
        lines.append(
            f"| {flag}`{short_name}` | `{it['dimensions_or_pages']}` | `{it['size_kb']} KB` | `{it['gemini_tokens']:,}` | `{it['claude_tokens']:,}` | `{it['openai_tokens']:,}` | {it['recommendation']} |"
        )
    return "\n".join(lines)


def main() -> int:
    _configure_utf8()
    parser = argparse.ArgumentParser(description="Estimate vision & PDF multimodal token cost across Gemini, Claude, and OpenAI.")
    parser.add_argument("targets", nargs="*", help="Media files or directories (defaults to workspace scan).")
    parser.add_argument("--workspace", "-w", default=".", help="Workspace root.")
    parser.add_argument("--format", choices=("markdown", "json"), default="markdown", help="Output format.")
    args = parser.parse_args()

    rep = scan_media_paths(args.targets, Path(args.workspace).resolve())
    if args.format == "json":
        print(json.dumps(rep, indent=2, ensure_ascii=False))
    else:
        print(render_markdown(rep))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
