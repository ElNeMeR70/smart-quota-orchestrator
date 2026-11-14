---
name: semantic-code-navigator
description: >-
  Ultra-low-token codebase discovery & impact analysis using SQLite FTS5 BM25
  symbol-chunk search and transitive reverse-import blast-radius calculation.
  Use when locating functions/classes in unfamiliar repos, finding where a
  feature is implemented, or selecting the minimal set of unit tests affected
  by a file change.
---

# Semantic Code Navigator (BM25 Search + Blast-Radius Engine)

Stop burning 20,000+ tokens on sequential `grep` + full-file reads or running 400 unrelated tests after editing one module!

## Bundled Zero-Dependency Engines (`./scripts/`)

| Engine | Script | What It Does |
| :--- | :--- | :--- |
| **1. BM25 Symbol-Chunk Search** | [search_code_bm25.py](./scripts/search_code_bm25.py) | Splits source files along function/class boundaries, ranks queries via SQLite FTS5 BM25, and returns top-K exact `file:Lstart-Lend` snippets in `<250` tokens (**90–97% savings**) |
| **2. Reverse-Import Blast Radius** | [analyze_blast_radius.py](./scripts/analyze_blast_radius.py) | Walks transitive reverse imports (`who imports X -> who imports Y`) to list direct importers, downstream files, and the **minimal affected unit test files** |

---

## Workflows

### 1. Pinpoint Any Feature or Symbol in `<250` Tokens
```bash
python "<skill_dir>/scripts/search_code_bm25.py" "verifyStripeWebhook jwt token" --workspace . --top-k 6
```
*(Or invoke the native MCP tool `sqo_code_search` directly!)*

### 2. Compute Blast Radius & Minimal Test Targets Before/After Editing
```bash
python "<skill_dir>/scripts/analyze_blast_radius.py" src/types/billing.ts src/auth/jwt.ts --workspace .
```
*(Or invoke the native MCP tool `sqo_blast_radius` directly!)*
Then run **only** the listed `affected_test_files` through `compact_command_output.py`!
