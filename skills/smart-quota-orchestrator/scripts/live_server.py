#!/usr/bin/env python3
"""Real-Time Localhost Web Command Center (`sqo serve`).

Launches a zero-dependency local web server (`http://127.0.0.1:7890`) powered purely
by Python's built-in `http.server` + `sqlite3`:
  - Live auto-refreshing $USD & Token ROI telemetry (`roi_ledger.db`)
  - Interactive Memory Vault Manager (Add / BM25 Search / Delete workspace memories in UI!)
  - Live Instant BM25 Codebase Symbol Search from the browser
  - Code-Graph Complexity × Fan-In Hotspots & Discovered API/UI Route Table
  - Instant Arabic (RTL) / English (LTR) UI toggle

Zero external dependencies. Pass `--dump-snapshot` for headless JSON verification in tests.
"""

from __future__ import annotations

import argparse
import importlib.util
import json
import sys
import urllib.parse
import webbrowser
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Any, Dict

SKILLS_ROOT = Path(__file__).resolve().parents[2]
SUITE_ROOT = SKILLS_ROOT.parent

_MOD_CACHE: Dict[str, Any] = {}


def _load_mod(rel_path: str):
    if rel_path not in _MOD_CACHE:
        target = SKILLS_ROOT / rel_path
        spec = importlib.util.spec_from_file_location(rel_path.replace("/", "_"), target)
        assert spec and spec.loader
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        _MOD_CACHE[rel_path] = mod
    return _MOD_CACHE[rel_path]


def build_api_snapshot(workspace: Path, roi_db: Path | None = None) -> Dict[str, Any]:
    roi_mod = _load_mod("smart-quota-orchestrator/scripts/roi_ledger.py")
    tax_mod = _load_mod("prompt-tax-profiler/scripts/optimize_prompt_rules.py")
    cache_mod = _load_mod("prompt-tax-profiler/scripts/audit_cache_stability.py")
    graph_mod = _load_mod("semantic-code-navigator/scripts/code_graph.py")
    mem_mod = _load_mod("project-memory-vault/scripts/memory_vault.py")

    roi = roi_mod.summarize_roi(roi_db or roi_mod.default_ledger_path())
    tax = tax_mod.profile_workspace(workspace)
    cache = cache_mod.audit_cache_stability(workspace)
    hotspots = graph_mod.analyze_hotspots(workspace, top_k=8)
    routes = graph_mod.extract_all_routes(workspace)
    mem_db = mem_mod._resolve_db_path(workspace)
    memories = mem_mod.list_facts(mem_db, limit=25)

    return {
        "version": "11.0.0",
        "workspace": str(workspace).replace("\\", "/"),
        "roi": roi,
        "prompt_tax": {
            "grade": tax["grade"],
            "always_on_tokens": tax["always_on_tokens_per_turn"],
            "skill_index_tokens": tax["skill_index_tokens_per_turn"],
            "skill_count": len(tax["skills"]),
        },
        "kv_cache": {
            "score": cache["cache_stability_score"],
            "status": cache["status"],
        },
        "hotspots": hotspots["top_hotspots"],
        "graph_sync": hotspots["sync_stats"],
        "routes": routes["routes"][:40],
        "memories": memories,
    }


LIVE_UI_HTML = """<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>Smart Quota OS v6.0 — Live Command Center</title>
  <style>
    :root {
      --bg: #070b19; --card: rgba(17, 24, 39, 0.88); --border: rgba(56, 189, 248, 0.24);
      --text: #f1f5f9; --muted: #94a3b8; --cyan: #38bdf8; --emerald: #34d399; --amber: #fbbf24; --violet: #a78bfa; --rose: #fb7185;
    }
    * { box-sizing: border-box; }
    body { margin: 0; padding: 26px 20px; font-family: Inter, "Segoe UI", Tahoma, sans-serif; background: radial-gradient(circle at top right, #1e1b4b, var(--bg) 60%); color: var(--text); }
    .wrap { max-width: 1200px; margin: 0 auto; }
    header { display: flex; justify-content: space-between; align-items: center; gap: 12px; flex-wrap: wrap; padding-bottom: 16px; margin-bottom: 22px; border-bottom: 1px solid var(--border); }
    h1 { margin: 0; font-size: 1.45rem; background: linear-gradient(90deg, var(--cyan), var(--emerald)); -webkit-background-clip: text; -webkit-text-fill-color: transparent; }
    .sub { color: var(--muted); font-size: 0.85rem; margin-top: 4px; }
    .btn { background: #1e293b; color: var(--text); border: 1px solid var(--border); padding: 8px 14px; border-radius: 10px; cursor: pointer; font-weight: 600; font-size: 0.85rem; }
    .btn.primary { background: linear-gradient(90deg, #0284c7, #059669); border: none; color: #fff; }
    .btn.danger { background: rgba(251,113,133,0.16); border-color: rgba(251,113,133,0.4); color: var(--rose); padding: 4px 9px; font-size: 0.78rem; }
    .kpis { display: grid; grid-template-columns: repeat(auto-fit, minmax(220px, 1fr)); gap: 14px; margin-bottom: 20px; }
    .card { background: var(--card); border: 1px solid var(--border); border-radius: 16px; padding: 18px; box-shadow: 0 12px 30px rgba(0,0,0,0.35); margin-bottom: 18px; }
    .k-lbl { color: var(--muted); font-size: 0.78rem; text-transform: uppercase; letter-spacing: 0.05em; }
    .k-val { font-size: 1.75rem; font-weight: 800; color: var(--cyan); margin: 6px 0 2px; }
    .k-sub { font-size: 0.82rem; color: var(--emerald); }
    .two-col { display: grid; grid-template-columns: repeat(auto-fit, minmax(460px, 1fr)); gap: 18px; }
    h2 { margin: 0 0 12px; font-size: 1.05rem; color: #fff; }
    input, select { background: #0f172a; color: var(--text); border: 1px solid #334155; border-radius: 9px; padding: 8px 11px; font-size: 0.88rem; }
    .row { display: flex; gap: 8px; flex-wrap: wrap; margin-bottom: 12px; }
    table { width: 100%; border-collapse: collapse; font-size: 0.86rem; }
    th, td { padding: 8px 6px; border-bottom: 1px solid rgba(148,163,184,0.14); text-align: inherit; }
    th { color: var(--muted); }
    code { background: #0f172a; color: var(--cyan); padding: 2px 6px; border-radius: 5px; font-size: 0.82rem; }
    .badge { display: inline-block; padding: 2px 8px; border-radius: 99px; font-size: 0.74rem; font-weight: 700; background: rgba(52,211,153,0.16); color: var(--emerald); }
    pre { background: #090d16; padding: 10px; border-radius: 10px; overflow-x: auto; font-size: 0.8rem; color: #cbd5e1; border: 1px solid #1e293b; }
  </style>
</head>
<body>
  <div class="wrap">
    <header>
      <div>
        <h1 id="title">⚡ Smart Quota & Swarm Orchestrator v6.0 — Live Command Center</h1>
        <div class="sub" id="wsMeta">Connecting to local SQLite telemetry...</div>
      </div>
      <div style="display:flex;gap:8px;align-items:center;">
        <span class="badge" id="liveDot">● LIVE (5s)</span>
        <button class="btn" onclick="toggleLang()" id="langBtn">🇸🇦 العربية</button>
        <button class="btn primary" onclick="refreshAll()" id="refBtn">↻ Refresh</button>
      </div>
    </header>

    <div class="kpis">
      <div class="card"><div class="k-lbl" data-i18n="k1">Prevented Token Waste</div><div class="k-val" id="vTok">0</div><div class="k-sub" id="vInt">0 autonomous interceptions</div></div>
      <div class="card"><div class="k-lbl" data-i18n="k2">Estimated API $USD Saved</div><div class="k-val" id="vUsd">$0.00</div><div class="k-sub" id="vOpus">Up to $0.00 (Frontier Tier)</div></div>
      <div class="card"><div class="k-lbl" data-i18n="k3">KV-Cache Prefix Stability</div><div class="k-val" id="vCache">100/100</div><div class="k-sub" id="vCacheSt">OPTIMAL (90% Discount Safe)</div></div>
      <div class="card"><div class="k-lbl" data-i18n="k4">Prompt Architecture Grade</div><div class="k-val" id="vGrade">A+</div><div class="k-sub" id="vTax">Always-on rule tax</div></div>
    </div>

    <div class="two-col">
      <div class="card">
        <h2 data-i18n="memTitle">🧠 Persistent Workspace Memory Vault (.sqo/memory.db)</h2>
        <div class="row">
          <select id="mCat"><option value="arch">arch</option><option value="auth">auth</option><option value="db">db</option><option value="gotcha">gotcha</option></select>
          <input id="mTitle" placeholder="Fact title (e.g. Stripe raw body)" style="flex:1;" />
          <input id="mDetail" placeholder="Concise detail & file:line..." style="flex:1.4;" />
          <button class="btn primary" onclick="addMemory()">+ Save</button>
        </div>
        <table><thead><tr><th>Category</th><th>Memory</th><th></th></tr></thead><tbody id="memBody"></tbody></table>
      </div>

      <div class="card">
        <h2 data-i18n="searchTitle">🔎 Instant SQLite FTS5 BM25 Symbol Search</h2>
        <div class="row">
          <input id="qInput" placeholder="Search symbol, function, route, or logic..." style="flex:1;" onkeydown="if(event.key==='Enter')runSearch()" />
          <button class="btn primary" onclick="runSearch()">BM25 Search</button>
        </div>
        <div id="searchOut"><div class="sub">Enter any query above to locate exact file:Lstart-Lend chunks in &lt;20ms.</div></div>
      </div>
    </div>

    <div class="two-col">
      <div class="card">
        <h2 data-i18n="hotTitle">🔥 Top Code-Graph Hotspots (Complexity × Fan-In)</h2>
        <table><thead><tr><th>File</th><th>LOC</th><th>Branches</th><th>Fan-In</th><th>Score</th></tr></thead><tbody id="hotBody"></tbody></table>
      </div>
      <div class="card">
        <h2 data-i18n="routeTitle">🌐 Discovered Backend & UI Routes</h2>
        <table><thead><tr><th>Method</th><th>Path</th><th>Framework</th><th>Source</th></tr></thead><tbody id="routeBody"></tbody></table>
      </div>
    </div>
  </div>

<script>
let lang = 'en';
const dict = {
  ar: {
    title: '⚡ مركز القيادة الحي — Smart Quota & Swarm Orchestrator v6.0',
    k1: 'التوكنز التي تم إنقاذها تلقائياً', k2: 'التوفير المالي المقدر ($USD)', k3: 'ثبات بادئة الـ KV-Cache', k4: 'تقييم هندسة القواعد',
    memTitle: '🧠 بنك الذاكرة المعمارية الدائم (يُحقن تلقائياً عند بدء المحادثة)',
    searchTitle: '🔎 البحث الدلالي الفوري عن الدوال والرموز (SQLite BM25)',
    hotTitle: '🔥 أعقد الملفات وأكثرها ارتباطاً (Code Graph Hotspots)',
    routeTitle: '🌐 مسارات الـ API والشاشات المكتشفة تلقائياً'
  },
  en: {
    title: '⚡ Smart Quota & Swarm Orchestrator v6.0 — Live Command Center',
    k1: 'Prevented Token Waste', k2: 'Estimated API $USD Saved', k3: 'KV-Cache Prefix Stability', k4: 'Prompt Architecture Grade',
    memTitle: '🧠 Persistent Workspace Memory Vault (.sqo/memory.db)',
    searchTitle: '🔎 Instant SQLite FTS5 BM25 Symbol Search',
    hotTitle: '🔥 Top Code-Graph Hotspots (Complexity × Fan-In)',
    routeTitle: '🌐 Discovered Backend & UI Routes'
  }
};
function toggleLang() {
  lang = lang === 'en' ? 'ar' : 'en';
  document.documentElement.dir = lang === 'ar' ? 'rtl' : 'ltr';
  document.getElementById('langBtn').textContent = lang === 'ar' ? '🇬🇧 English' : '🇸🇦 العربية';
  document.getElementById('title').textContent = dict[lang].title;
  document.querySelectorAll('[data-i18n]').forEach(el => { el.textContent = dict[lang][el.dataset.i18n]; });
}
function esc(s) { const d = document.createElement('div'); d.textContent = s ?? ''; return d.innerHTML; }
async function refreshAll() {
  const res = await fetch('/api/overview');
  const d = await res.json();
  document.getElementById('wsMeta').textContent = `Workspace: ${d.workspace} • SQLite Graph Synced in ${d.graph_sync.sync_time_ms}ms (${d.graph_sync.total_indexed_files} files)`;
  document.getElementById('vTok').textContent = d.roi.total_tokens_saved.toLocaleString();
  document.getElementById('vInt').textContent = `${d.roi.total_interceptions} autonomous shield interceptions`;
  const bal = d.roi.usd_equivalents.balanced_sonnet_carbon.saved_usd.toFixed(2);
  const op = d.roi.usd_equivalents.frontier_opus_pro.saved_usd.toFixed(2);
  document.getElementById('vUsd').textContent = `$${bal}`;
  document.getElementById('vOpus').textContent = `Up to $${op} (Frontier Opus Tier)`;
  document.getElementById('vCache').textContent = `${d.kv_cache.score}/100`;
  document.getElementById('vCacheSt').textContent = d.kv_cache.status;
  document.getElementById('vGrade').textContent = d.prompt_tax.grade.split(' ')[0];
  document.getElementById('vTax').textContent = `~${d.prompt_tax.always_on_tokens} rule tok/turn • ${d.prompt_tax.skill_count} skills`;

  document.getElementById('memBody').innerHTML = d.memories.length ? d.memories.map(m =>
    `<tr><td><code>${esc(m.category)}</code></td><td><strong>${esc(m.title)}</strong><br/><span class="sub">${esc(m.detail)}</span></td><td><button class="btn danger" onclick="delMem(${m.id})">✕</button></td></tr>`
  ).join('') : '<tr><td colspan="3" class="sub">No memories stored yet — add one above!</td></tr>';

  document.getElementById('hotBody').innerHTML = d.hotspots.map(h =>
    `<tr><td><code>${esc(h.file)}</code></td><td>${h.loc}</td><td>${h.cyclomatic_complexity}</td><td>${h.fan_in}</td><td><strong>${h.hotspot_score}</strong></td></tr>`
  ).join('');

  document.getElementById('routeBody').innerHTML = d.routes.length ? d.routes.map(r =>
    `<tr><td><span class="badge">${esc(r.method)}</span></td><td><code>${esc(r.path)}</code></td><td>${esc(r.framework)}</td><td><code>${esc(r.file)}:L${r.line}</code></td></tr>`
  ).join('') : '<tr><td colspan="4" class="sub">No HTTP/UI routes detected in current scope.</td></tr>';
}
async function addMemory() {
  const category = document.getElementById('mCat').value;
  const title = document.getElementById('mTitle').value.trim();
  const detail = document.getElementById('mDetail').value.trim();
  if (!title || !detail) return;
  await fetch('/api/memories', { method: 'POST', headers: {'Content-Type':'application/json'}, body: JSON.stringify({category, title, detail}) });
  document.getElementById('mTitle').value = ''; document.getElementById('mDetail').value = '';
  refreshAll();
}
async function delMem(id) {
  await fetch(`/api/memories?id=${id}`, { method: 'DELETE' });
  refreshAll();
}
async function runSearch() {
  const q = document.getElementById('qInput').value.trim();
  if (!q) return;
  const res = await fetch(`/api/search?q=${encodeURIComponent(q)}`);
  const d = await res.json();
  document.getElementById('searchOut').innerHTML = `<div class="sub" style="margin-bottom:8px;">Saved <strong>${d.token_savings_pct}%</strong> tokens (${d.returned_approx_tokens} tok vs ${d.naive_repo_tokens} naive)</div>` +
    d.results.map(r => `<div style="margin-bottom:8px;"><code>${esc(r.file)}:L${r.start_line}-L${r.end_line}</code> <strong>${esc(r.symbol)}</strong><pre>${esc(r.preview)}</pre></div>`).join('');
}
refreshAll();
setInterval(refreshAll, 5000);
</script>
</body>
</html>
"""


def make_handler(workspace: Path):
    mem_mod = _load_mod("project-memory-vault/scripts/memory_vault.py")
    bm25_mod = _load_mod("semantic-code-navigator/scripts/search_code_bm25.py")

    class SQOHandler(BaseHTTPRequestHandler):
        def log_message(self, fmt: str, *args: Any) -> None:
            return  # Quiet clean console

        def _send_json(self, data: Any, status: int = 200) -> None:
            body = json.dumps(data, ensure_ascii=False).encode("utf-8")
            self.send_response(status)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)

        def do_GET(self) -> None:
            parsed = urllib.parse.urlparse(self.path)
            if parsed.path == "/api/overview":
                self._send_json(build_api_snapshot(workspace))
                return
            if parsed.path == "/api/search":
                qs = urllib.parse.parse_qs(parsed.query)
                q = (qs.get("q") or [""])[0]
                res = bm25_mod.search_workspace(workspace, q, top_k=5) if q else {"results": [], "token_savings_pct": 0, "returned_approx_tokens": 0, "naive_repo_tokens": 0}
                self._send_json(res)
                return
            html_bytes = LIVE_UI_HTML.encode("utf-8")
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.send_header("Content-Length", str(len(html_bytes)))
            self.end_headers()
            self.wfile.write(html_bytes)

        def do_POST(self) -> None:
            if self.path == "/api/memories":
                length = int(self.headers.get("Content-Length", "0"))
                payload = json.loads(self.rfile.read(length).decode("utf-8") or "{}")
                db_p = mem_mod._resolve_db_path(workspace)
                saved = mem_mod.remember_fact(
                    db_p,
                    str(payload.get("category", "arch")),
                    str(payload.get("title", "Note")),
                    str(payload.get("detail", "")),
                    payload.get("files") or [],
                )
                self._send_json({"ok": True, "saved": saved})
                return
            self._send_json({"error": "Not found"}, status=404)

        def do_DELETE(self) -> None:
            parsed = urllib.parse.urlparse(self.path)
            if parsed.path == "/api/memories":
                qs = urllib.parse.parse_qs(parsed.query)
                mid = int((qs.get("id") or ["0"])[0])
                db_p = mem_mod._resolve_db_path(workspace)
                ok = mem_mod.forget_fact(db_p, mid)
                self._send_json({"ok": ok})
                return
            self._send_json({"error": "Not found"}, status=404)

    return SQOHandler


def main() -> int:
    for s in (sys.stdout, sys.stderr):
        if hasattr(s, "reconfigure"):
            try:
                s.reconfigure(encoding="utf-8")
            except Exception:
                pass

    parser = argparse.ArgumentParser(description="Start the real-time Smart Quota OS localhost web command center.")
    parser.add_argument("--workspace", "-w", default=".", help="Workspace root to monitor.")
    parser.add_argument("--port", "-p", type=int, default=7890, help="Local HTTP port (default: 7890).")
    parser.add_argument("--open", action="store_true", help="Open default browser automatically.")
    parser.add_argument("--dump-snapshot", action="store_true", help="Print JSON overview snapshot and exit immediately (for CI/testing).")
    args = parser.parse_args()

    ws = Path(args.workspace).resolve()
    if args.dump_snapshot:
        print(json.dumps(build_api_snapshot(ws), indent=2, ensure_ascii=False))
        return 0

    url = f"http://127.0.0.1:{args.port}"
    server = ThreadingHTTPServer(("127.0.0.1", args.port), make_handler(ws))
    print(f"⚡ Smart Quota OS v6.0 Live Command Center running at: {url}")
    print(f"   Monitoring workspace: {ws} (Press Ctrl+C to stop)")
    if args.open:
        webbrowser.open(url)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
