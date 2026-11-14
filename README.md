<div align="center">

<img src="./assets/logo.svg" alt="Smart Quota & Swarm Orchestrator Logo" width="115" height="115" />

# Smart Quota & Swarm Orchestrator (`v4.0` Autonomous Agent OS)

**The Zero-Dependency Autonomous Lifecycle Shield, 14-Tool Native MCP Server, Incremental SQLite Code Graph & Multi-Agent Quota Optimizer for Google Antigravity, Claude Code, Cursor, VS Code, Gemini CLI & Windsurf**

[![Version](https://img.shields.io/badge/Release-v4.0.0_Autonomous_OS-6366F1?style=for-the-badge)](https://github.com/ElNeMeR70/smart-quota-orchestrator)
[![MCP Server](https://img.shields.io/badge/MCP_Tools-14_Native_Tools-10B981?style=for-the-badge)](./mcp_server.py)
[![Lifecycle Engine](https://img.shields.io/badge/Stateful_Hooks-SessionStart_%7C_Pre_%7C_Post-F59E0B?style=for-the-badge)](./hooks/token_shield_hook.py)
[![Python 3.9+](https://img.shields.io/badge/Python-3.9%2B_Zero_Deps-38BDF8?style=for-the-badge)](./pyproject.toml)
[![License: MIT](https://img.shields.io/badge/License-MIT-A855F7?style=for-the-badge)](./LICENSE)

[**English Overview**](#-what-makes-v40-an-autonomous-agent-os) • [**14 Native MCP Tools**](#-14-native-mcp-tools-sqo-engine) • [**3-Stage Stateful Shield**](#️-3-stage-stateful-lifecycle-engine-hooksjson) • [**Quick Install**](#-quick-installation) • [**CLI Reference (25 Commands)**](#-unified-sqo-cli--pipx--uv-tool-25-commands) • [**الشرح بالعربية**](#-الدليل-العربي-الكامل-الإصدار-الرابع-v40)

</div>

---

## 🔥 What Makes `v4.0` an Autonomous Agent OS?

Most "agent skills" are passive Markdown files hoping the LLM obeys them. **Smart Quota & Swarm Orchestrator `v4.0`** operates as a **self-enforcing runtime layer** between your AI coding agent and your codebase—combining **stateful `SessionStart` / `PreToolUse` / `PostToolUse` hooks**, a **14-tool zero-dependency JSON-RPC MCP server**, an **incremental `mtime_ns` SQLite Code Graph**, and **KV-Cache prefix stability auditing**:

| Real-World Quota Killer | Naive Agent Cost | `v4.0` Autonomous Defense | Verified Savings |
| :--- | :--- | :--- | :--- |
| **Cold-start codebase re-discovery every chat** | `8,000 – 25,000` tokens | **`SessionStart` Warm Memory Hook** auto-injects recalled facts from `.sqo/memory.db` on Turn 0 | **100% zero cold-start waste** |
| **Re-reading the exact same unchanged file 3–5×** | `5,000 – 30,000` tokens | **Stateful `PreToolUse` Deduplicator** tracks `(path, mtime_ns, range)` per session & unlocks on `edit_file` | **100% duplicate-read elimination** |
| **Blind full-file read on a 2,500-line monolith** | `18,000+` tokens | **Giant-Source Auto-Clamper** rewrites `overwrite: {"StartLine": 1, "EndLine": 280}` on the fly | **85%–92% fewer tokens** |
| **Reading `package-lock.json` / `.min.js` / `.map`** | `45,000 – 180,000` tokens | **Token-Bomb Blocker** denies unbounded `>50KB` lockfile/bundle reads & `cat` dumps in `<10ms` | **100% prevented** |
| **Running the exact same failing test 5× in a row** | `15,000+` tokens | **Blind Retry-Loop Breaker** halts the 3rd identical failing command when no file was edited | **Stops runaway burn loops** |
| **Chasing a 6-frame crash traceback file by file** | `6` turns + `14,000` tokens | **`sqo_pinpoint_error`** extracts exact `±10` line windows across every local crash frame in **1 call** | **93% fewer tokens & 1 turn** |
| **Busting the 90% LLM Prompt KV-Cache discount** | **10×** higher input billing | **`sqo_cache_audit`** flags volatile `PreInvocation` timestamps/UUIDs & unsorted walks | **Preserves 90% KV-cache hit rate** |

---

## 🛡️ 3-Stage Stateful Lifecycle Engine (`hooks.json`)

Powered by [`hooks/token_shield_hook.py`](./hooks/token_shield_hook.py) (`<15ms` execution, pure Python stdlib, fail-open safety):

1. **`SessionStart` (Zero-Turn Warm Recall)**: Reads up to 8 stored architectural decisions/gotchas from `.sqo/memory.db` once at Turn 0 (`injectSteps`)—preserving 100% prompt KV-cache prefix stability across subsequent turns.
2. **`PreToolUse` (4-in-1 Active Shield)**:
   - **Token-Bomb Hard Blocker**: Blocks unbounded reads or `cat`/`Get-Content` dumps of `package-lock.json`, `pnpm-lock.yaml`, `yarn.lock`, `pubspec.lock`, `Cargo.lock`, `.map`, and `.min.js` (`>= 50 KB`).
   - **Stateful Duplicate-Read Deduplicator**: Blocks redundant `read_file` calls when `(file_path, mtime_ns, size, StartLine, EndLine)` hasn't changed since an earlier step in the same conversation.
   - **Giant Source Auto-Clamper (`overwrite`)**: Automatically clamps blind full-file reads on `>55 KB` & `>1,200`-line code files to `StartLine: 1, EndLine: 280`.
   - **Blind Retry-Loop Breaker**: Blocks a 3rd consecutive identical failing `run_command` if zero files were edited in between.
3. **`PostToolUse` (Live Ledger Sync)**: Records successful read signatures, unlocks files immediately upon `edit_file`/`write_file`, and tracks command failure streaks.

---

## 🔌 14 Native MCP Tools (`sqo-engine`)

Zero `pip install` required—[`mcp_server.py`](./mcp_server.py) speaks native MCP `2025-03-26` JSON-RPC over `stdio`:

| MCP Tool | Capability |
| :--- | :--- |
| **`sqo_code_search`** | SQLite FTS5 BM25 symbol-boundary code search (`<250` tokens vs `20K+` full-file reads) |
| **`sqo_smart_outline`** | AST + multi-language structural skeletonizer & single-symbol surgical extractor |
| **`sqo_context_pack`** | Token-budgeted multi-file context bundler (full core files + AST outlines for neighbors) |
| **`sqo_blast_radius`** | Transitive reverse-import impact graph + **minimal affected unit test selector** |
| **`sqo_pinpoint_error`** | **NEW `v4.0`** — 1-shot multi-file crash stack-trace code window extractor (Python, JS/TS, Dart, Go, Rust, PHP) |
| **`sqo_code_hotspots`** | **NEW `v4.0`** — Incremental `mtime_ns` SQLite Code Graph: **Cyclomatic Complexity × Fan-In** hotspots & orphan modules |
| **`sqo_api_routes`** | **NEW `v4.0`** — Multi-framework HTTP/UI route table mapper (Next.js, Express/Fastify, NestJS, FastAPI/Flask, Laravel, Go, Flutter) |
| **`sqo_memory_vault`** | Persistent cross-session SQLite FTS5 architectural memory (`remember` / `recall` / `list` / `forget`) |
| **`sqo_dependency_slices`** | Zero-conflict parallel worker file partitioning (`Stage-0` contracts + `Stage-1` slices) |
| **`sqo_budgeted_diff`** | Lockfile-stripping, token-capped Git diff compressor for ultra-cheap PR reviews |
| **`sqo_secret_scrub`** | 10-pattern credential, JWT, DSN, private-key & `.env` redactor/auditor |
| **`sqo_cache_audit`** | **NEW `v4.0`** — LLM Prompt KV-Cache prefix stability auditor (`0–100` score) |
| **`sqo_quota_pools`** | Live shared-pool detector, reset countdown & safe `%/hr` burn-rate calculator |
| **`sqo_benchmark`** | Empirical Before-vs-After token compression benchmark on any workspace |

---

## 📦 Complete Suite Architecture (6 Skills + 3 Subagents + MCP + Hooks)

```text
smart-quota-orchestrator/
├── plugin.json                        # Google Antigravity Plugin v4.0.0
├── .claude-plugin/plugin.json         # Claude Code Plugin v4.0.0
├── gemini-extension.json              # Gemini CLI Extension v4.0.0
├── pyproject.toml                     # pip / pipx / uv tool installable (`sqo` CLI)
├── mcp_config.json & mcp_server.py    # Zero-Dependency 14-Tool Native MCP Server
├── hooks.json & hooks/                # 3-Stage Stateful Lifecycle Engine (SessionStart/Pre/Post)
├── sqo.py                             # Unified 25-Command Developer CLI
├── rules/AGENTS.md                    # Crisp Always-On Guardrails (Grade A+: ~315 tokens/turn)
├── agents/                            # 3 Specialist Read-Only Subagents
│   ├── codebase-scout.md              # BM25, Code-Graph & Stack-Trace Recon Scout
│   ├── quota-planner.md               # Parallel Slice & Budget Architect
│   └── token-auditor.md               # Prompt-Tax, KV-Cache & Session-Leak Auditor
└── skills/                            # 6 Progressive-Disclosure Skills (20 Engines)
    ├── smart-quota-orchestrator/      # Pools, Complexity, Sim, Benchmark, Audit, HTML, 5-IDE Sync
    ├── semantic-code-navigator/       # BM25 Search, Blast Radius, SQLite Code Graph, Stack Pinpoint
    ├── context-compactor/             # AST Outline, Context Pack, Diff, Denoise, Ignore, Handoff
    ├── project-memory-vault/          # Cross-Session SQLite FTS5 Memory + Secret Redactor
    ├── parallel-slice-architect/      # Import-Graph Partitioner + Workflow Generator
    └── prompt-tax-profiler/           # Static Rule Profiler + KV-Cache Stability Auditor
```

---

## 🚀 Quick Installation

### 1. Google Antigravity (Full Plugin: 14 MCP Tools + Stateful Hooks + 6 Skills + 3 Subagents)
```powershell
git clone https://github.com/ElNeMeR70/smart-quota-orchestrator.git
cd smart-quota-orchestrator

# Windows PowerShell
powershell -ExecutionPolicy Bypass -File .\install.ps1

# macOS / Linux
bash ./install.sh
```

### 2. Wire Any Workspace Across All 5 AI IDEs in One Command!
Configures **Antigravity** (`.agentignore`), **Cursor** (`.cursor/mcp.json` + `.cursorignore`), **Claude Code** (`.mcp.json` + `.claudeignore`), **VS Code** (`.vscode/mcp.json`), and **Windsurf** (`.codeiumignore`):
```bash
python sqo.py sync-ide --workspace /path/to/your/project --ides all
```

### 3. Install `sqo` Globally via `uv` or `pipx` (or `npx skills`)
```bash
uv tool install git+https://github.com/ElNeMeR70/smart-quota-orchestrator.git
# or: npx skills add ElNeMeR70/smart-quota-orchestrator
```

---

## 💻 Unified `sqo` CLI & `pipx` / `uv tool` (25 Commands)

```bash
# 🩺 Full Workspace Health + Prompt-Tax + KV-Cache Stability + Live Benchmark
python sqo.py doctor --workspace .

# 🔥 Incremental SQLite Code Graph: Complexity × Coupling Hotspots & API Route Table
python sqo.py hotspots --workspace . --top-k 10
python sqo.py routes --workspace .

# 🎯 1-Step Crash Stack-Trace Code Window Pinpointer
python sqo.py pinpoint --workspace . --trace-file crash.log

# ⚡ KV-Cache Prefix Stability Audit & 5-IDE Shield Sync
python sqo.py cache-audit --workspace .
python sqo.py sync-ide --workspace . --ides all

# 🔎 BM25 Symbol Search, Blast Radius & Persistent Memory Vault
python sqo.py search "verifyWebhookSignature" --workspace .
python sqo.py blast src/auth/jwt.ts --workspace .
python sqo.py memory --workspace . remember --category arch --title "Auth flow" --detail "Uses Ed25519 JWT"

# 📊 Interactive HTML Telemetry Dashboard & 22-Test Suite
python sqo.py dashboard --workspace . --output quota-dashboard.html
python -m unittest discover -s tests -v
```

---

<div dir="rtl">

## 🌍 الدليل العربي الكامل (الإصدار الرابع `v4.0` — نظام التشغيل الذاتي للوكلاء)

تُعد منظومة **Smart Quota & Swarm Orchestrator `v4.0`** أول نظام تشغيل ذاتي متكامل ومجاني بدون أي مكتبات خارجية (`Zero Dependencies`) يحمي الكوتا والتوكنز تلقائياً أثناء عمل الوكيل الذكي عبر **4 طبقات حماية وهندسة سياق متقدمة**:

### أبرز اختراقات الإصدار `v4.0` الجديد:
1. **محرك الحماية التلقائي ثلاثي المراحل (`SessionStart` + `PreToolUse` + `PostToolUse`)**:
   - **`SessionStart` (استدعاء الذاكرة الفوري)**: يحقن أهم الحقائق المعمارية المخزنة في `.sqo/memory.db` مرة واحدة فقط في بداية المحادثة لتوفير جولات الاستكشاف المتكررة مع الحفاظ بنسبة **100%** على خصم الـ **KV-Cache (90%)**.
   - **`PreToolUse` (مانع التكرار + التقليم التلقائي + كاسر الحلقات المفرغة)**: يمنع إعادة قراءة أي ملف لم يتغير على القرص (`mtime_ns`)، ويقلّم تلقائياً القراءات العمياء للملفات العملاقة (`>1,200` سطر) إلى أول `280` سطر (`overwrite`)، ويمنع قراءة ملفات القفل (`package-lock.json` / `.map`)، ويوقف تكرار نفس الأمر الفاشل للمرة الثالثة دون تعديل الكود!
   - **`PostToolUse`**: يحدّث سجل البصمات الزمنية للملفات ويفتح القفل فوراً بمجرد تعديل الملف عبر `edit_file`.
2. **خادم MCP أصلي يضم 14 أداة ذكية (`sqo-engine`)**:
   - أضفنا في `v4.0`: أداة **`sqo_pinpoint_error`** لاستخراج أسطر الخطأ من أي Stack Trace متعدد الملفات في خطوة واحدة، وأداة **`sqo_code_hotspots`** لبناء رسم بياني تزايدي بـ SQLite يكشف أعقد الملفات وأكثرها ارتباطاً، وأداة **`sqo_api_routes`** لاستخراج كافة مسارات الـ API والواجهات، وأداة **`sqo_cache_audit`** لفحص ثبات بادئة الـ KV-Cache.
3. **مزامنة شاملة لـ 5 بيئات برمجة بضغطة واحدة (`sqo sync-ide`)**:
   - يربط خادم `sqo-engine` وملفات التجاهل تلقائياً في **Antigravity** و**Cursor** و**Claude Code** و**VS Code** و**Windsurf**، بالإضافة لدعم التثبيت كأداة نظام عبر `pyproject.toml` (`uv tool` / `pipx`).

</div>
