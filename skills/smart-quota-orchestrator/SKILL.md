---
name: smart-quota-orchestrator
description: >-
  Autonomous AI Agent OS & multi-agent quota orchestration engine (v4.0) with
  14 native MCP tools, a 3-stage stateful lifecycle shield (SessionStart warm
  memory + PreToolUse deduplicator/auto-clamper/loop-breaker + PostToolUse
  ledger), cross-IDE config sync, live quota pool analytics, complexity scoring,
  monolith-vs-swarm simulation, empirical benchmarks, and HTML telemetry. Use
  when checking or optimizing model quota, choosing thinking levels, syncing IDE
  shields, benchmarking workspace token savings, or orchestrating parallel agents.
---

# Smart Quota & Swarm Orchestrator (`v4.0` Autonomous Agent OS)

Maximize engineering output per quota unit across **four active defense layers**:
1. **3-Stage Stateful Lifecycle Engine (`hooks.json`)**:
   - **`SessionStart`**: Auto-injects recalled architectural facts from `.sqo/memory.db` on Turn 0 (`0` re-discovery turns, `100%` KV-cache prefix friendly).
   - **`PreToolUse`**: Blocks `>50KB` lockfile/sourcemap bombs, **deduplicates unchanged re-reads** per `conversationId`, **auto-clamps** blind full reads on `>1,200`-line source files (`overwrite: StartLine 1..280`), and **breaks 3x blind command retry loops**.
   - **`PostToolUse`**: Maintains the `mtime_ns` file-read ledger and resets locks automatically whenever files are edited.
2. **14 Native Zero-Dependency MCP Tools (`sqo-engine`)**: `sqo_code_search`, `sqo_smart_outline`, `sqo_context_pack`, `sqo_blast_radius`, `sqo_pinpoint_error`, `sqo_code_hotspots`, `sqo_api_routes`, `sqo_memory_vault`, `sqo_dependency_slices`, `sqo_budgeted_diff`, `sqo_secret_scrub`, `sqo_cache_audit`, `sqo_quota_pools`, `sqo_benchmark`.
3. **Multi-Model & Parallel Routing (`./scripts/`)**: Pairs frontier planners (`Carbon`, `Argon`, `Opus`) with fast execution models (`Hydrogen`, `Orchestrator`, `flash` workflows).
4. **Universal 5-IDE Shield Synchronizer**: Wires `sqo-engine` MCP + ignore shields across Antigravity, Cursor, Claude Code, VS Code, and Windsurf in 1 command.

---

## Bundled CLI Engines (`./scripts/`)

| Engine | Script | Purpose |
| :--- | :--- | :--- |
| **1. Live Quota Pool Analyzer** | [parse_quota_pools.py](./scripts/parse_quota_pools.py) | Groups shared vs. independent reserve model pools, reset countdowns & safe `%/hr` burn ceiling |
| **2. Task Complexity & Topology Scorer** | [analyze_task_complexity.py](./scripts/analyze_task_complexity.py) | Computes Complexity (`0–100`) & Parallelizability (`0.0–1.0`) + flags security/payment/DB risks |
| **3. Monolith vs. Swarm Simulator** | [simulate_workflow_cost.py](./scripts/simulate_workflow_cost.py) | Quantifies $O(T^2)$ cumulative context burn vs `Orchestrator` & `run_workflow(model='flash')` |
| **4. Empirical Compression Benchmark** | [benchmark_suite.py](./scripts/benchmark_suite.py) | Runs real measurements on the active workspace and prints verified token reduction percentages |
| **5. Session Transcript Leak Auditor** | [audit_session_burn.py](./scripts/audit_session_burn.py) | Scans Antigravity / Claude Code JSONL logs for duplicate unchanged reads & retry loops |
| **6. Interactive HTML Telemetry Center** | [generate_html_dashboard.py](./scripts/generate_html_dashboard.py) | Generates a standalone dark-glassmorphism `quota-dashboard.html` report |
| **7. Universal 5-IDE Config Synchronizer** | [sync_ide_configs.py](./scripts/sync_ide_configs.py) | Wires `sqo-engine` MCP + `.agentignore`/`.cursorignore`/`.claudeignore`/`.codeiumignore` |

---

## Core Workflows

### 1. Live Quota Pool Inspection & Failover Strategy
In **Google Antigravity**, call `swarm(action="models", all=true)` and pass the JSON to `sqo_quota_pools` (or `parse_quota_pools.py`):
- **`HEALTHY (>50%)`**: Default complex builds to **Orchestrator (Carbon)** or **Orchestrator (Argon)**; reserve standalone **Carbon (High)** strictly for deep security/architecture.
- **`CONSERVE (20%–50%)`**: Prefer **Orchestrator (Argon)** and fan out multi-file tasks via `run_workflow(model="flash")`.
- **`CRITICAL (<20%)`**: Use **Hydrogen (`Medium` or `XHigh`)** until reset, or notify the user of untouched reserve pools (`Claude 4.6`, `GPT-OSS 120B`).
- Full matrix: [references/model-routing-matrix.md](./references/model-routing-matrix.md).

### 2. Sync All 5 AI IDEs, Benchmark & Generate Telemetry
```bash
# Wire MCP server + ignore shields across Antigravity, Cursor, Claude Code, VS Code & Windsurf
python "<skill_dir>/scripts/sync_ide_configs.py" --workspace . --ides all

# Run live Before-vs-After token compression benchmark + HTML telemetry dashboard
python "<skill_dir>/scripts/benchmark_suite.py" --workspace .
python "<skill_dir>/scripts/generate_html_dashboard.py" --workspace . --output quota-dashboard.html
```
For parallel `run_workflow` & `swarm` templates, read [references/parallel-workflow-patterns.md](./references/parallel-workflow-patterns.md).
