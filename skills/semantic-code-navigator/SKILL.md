---
name: semantic-code-navigator
description: >-
  Ultra-low-token codebase discovery, incremental SQLite code-graph hotspot &
  API route mapping, 1-turn crash stack-trace pinpointing, SQLite FTS5 BM25
  symbol search, and transitive reverse-import blast-radius calculation. Use
  when locating symbols, mapping HTTP/UI endpoints, debugging stack traces,
  finding complexity hotspots, or selecting minimal affected unit tests.
---

# Semantic Code Navigator (`v4.0` Code Intelligence Engine)

Stop burning 25,000+ tokens on sequential `grep` + full-file reads, multi-turn traceback chasing, or running 400 unrelated tests after editing one module!

## Bundled Zero-Dependency Engines (`./scripts/`)

| Engine | Script | Native MCP Tool | What It Does |
| :--- | :--- | :--- | :--- |
| **1. BM25 Symbol-Chunk Search** | [search_code_bm25.py](./scripts/search_code_bm25.py) | `sqo_code_search` | Splits source files along function/class boundaries, ranks queries via SQLite FTS5 BM25, and returns top-K exact `file:Lstart-Lend` snippets in `<250` tokens (**90–97% savings**) |
| **2. Reverse-Import Blast Radius** | [analyze_blast_radius.py](./scripts/analyze_blast_radius.py) | `sqo_blast_radius` | Walks transitive reverse imports (`who imports X -> who imports Y`) to list direct importers, downstream files, and the **minimal affected unit test files** |
| **3. Incremental SQLite Code Graph** | [code_graph.py](./scripts/code_graph.py) | `sqo_code_hotspots`, `sqo_api_routes` | `mtime_ns`-cached SQLite graph (`.sqo/code_graph.db`) computing **Cyclomatic Complexity × Fan-In Bug Hotspots**, unimported modules, and multi-framework **API/UI Route tables** (Next.js, Express/Fastify, NestJS, FastAPI/Flask, Laravel, Go, Flutter) |
| **4. 1-Turn Stack-Trace Pinpointer** | [pinpoint_stacktrace.py](./scripts/pinpoint_stacktrace.py) | `sqo_pinpoint_error` | Parses Python, JS/TS V8, Dart/Flutter, Go, Rust, and PHP stack traces, skips `node_modules`/`site-packages`, and extracts exact `±10` line windows around every local frame in **1 step** |

---

## Core Workflows

### 1. Pinpoint Any Feature or Symbol in `<250` Tokens
```bash
python "<skill_dir>/scripts/search_code_bm25.py" "verifyStripeWebhook jwt token" --workspace . --top-k 6
```

### 2. Map Bug Hotspots & All API/UI Routes Instantly
```bash
python "<skill_dir>/scripts/code_graph.py" hotspots --workspace . --top-k 10
python "<skill_dir>/scripts/code_graph.py" routes --workspace .
```

### 3. Extract Multi-File Crash Windows From Any Stack Trace in 1 Step
```bash
python "<skill_dir>/scripts/pinpoint_stacktrace.py" --workspace . --trace-file crash.log
```

### 4. Compute Blast Radius & Minimal Test Targets Before/After Editing
```bash
python "<skill_dir>/scripts/analyze_blast_radius.py" src/types/billing.ts src/auth/jwt.ts --workspace .
```
Then run **only** the listed `affected_test_files` through `compact_command_output.py`!
