---
name: smart-quota-orchestrator
description: >-
  Autonomous AI Agent OS (v5.0) with 16 native MCP tools, 3-stage stateful
  lifecycle shield, live $USD & token ROI ledger, 5-IDE config sync, Git
  pre-commit guard, quota pool analytics, complexity scoring, swarm simulation,
  and HTML telemetry.
---

# Smart Quota & Swarm Orchestrator (`v5.0` Autonomous Agent OS)

Maximize engineering output per quota unit across **five active defense layers**:
1. **3-Stage Stateful Lifecycle Engine (`hooks.json`)**:
   - **`SessionStart`**: Auto-injects recalled architectural facts from `.sqo/memory.db` on Turn 0 (`100%` KV-cache prefix friendly).
   - **`PreToolUse`**: Blocks `>50KB` lockfile/sourcemap bombs, **deduplicates unchanged re-reads** per `conversationId`, **auto-clamps** blind full reads on `>1,200`-line source files (`overwrite: StartLine 1..280`), and **breaks 3x blind command retry loops**—automatically logging every saved token to `roi_ledger.db`!
   - **`PostToolUse`**: Maintains the `mtime_ns` file-read ledger and unlocks files immediately on `edit_file`/`write_file`.
2. **16 Native Zero-Dependency MCP Tools (`sqo-engine`)**: `sqo_code_search`, `sqo_smart_outline`, `sqo_context_pack`, `sqo_blast_radius`, `sqo_pinpoint_error`, `sqo_code_hotspots`, `sqo_api_routes`, `sqo_memory_vault`, `sqo_dependency_slices`, `sqo_budgeted_diff`, `sqo_secret_scrub`, `sqo_cache_audit`, `sqo_quota_pools`, `sqo_benchmark`, `sqo_roi_ledger`, `sqo_media_budget`.
3. **Live `$USD` & Token ROI Ledger (`roi_ledger.py`)**: Quantifies cumulative prevented waste across Frontier (`$15/1M`), Balanced (`$3/1M`), and Fast (`$0.30/1M`) model tiers.
4. **Multi-Model & Parallel Routing (`./scripts/`)**: Pairs frontier planners (`Carbon`, `Argon`, `Opus`) with fast execution models (`Hydrogen`, `Orchestrator`, `flash` workflows).
5. **Universal 5-IDE Sync & Git Pre-Commit Guard**: Wires `sqo-engine` MCP + ignore shields across Antigravity, Cursor, Claude Code, VS Code & Windsurf, plus `<40ms` `.git/hooks/pre-commit` secret/prompt-tax protection.

---

## Bundled CLI Engines (`./scripts/`)

| Engine | Script / MCP Tool | Purpose |
| :--- | :--- | :--- |
| **1. Live Token & `$USD` ROI Ledger** | [roi_ledger.py](./scripts/roi_ledger.py) / `sqo_roi_ledger` | Tracks cumulative tokens & `$USD` saved by autonomous hooks and compression tools |
| **2. Live Quota Pool Analyzer** | [parse_quota_pools.py](./scripts/parse_quota_pools.py) / `sqo_quota_pools` | Groups shared vs. independent reserve model pools, reset countdowns & safe `%/hr` burn ceiling |
| **3. Task Complexity & Topology Scorer** | [analyze_task_complexity.py](./scripts/analyze_task_complexity.py) | Computes Complexity (`0–100`) & Parallelizability (`0.0–1.0`) + flags security/payment/DB risks |
| **4. Monolith vs. Swarm Simulator** | [simulate_workflow_cost.py](./scripts/simulate_workflow_cost.py) | Quantifies $O(T^2)$ cumulative context burn vs `Orchestrator` & `run_workflow(model='flash')` |
| **5. Empirical Compression Benchmark** | [benchmark_suite.py](./scripts/benchmark_suite.py) / `sqo_benchmark` | Runs real measurements on the active workspace and prints verified token reduction percentages |
| **6. Session Transcript Leak Auditor** | [audit_session_burn.py](./scripts/audit_session_burn.py) | Scans Antigravity / Claude Code JSONL logs for duplicate unchanged reads & retry loops |
| **7. Interactive HTML Telemetry Center** | [generate_html_dashboard.py](./scripts/generate_html_dashboard.py) | Generates a standalone dark-glassmorphism `quota-dashboard.html` report |
| **8. Universal 5-IDE Config Synchronizer** | [sync_ide_configs.py](./scripts/sync_ide_configs.py) | Wires `sqo-engine` MCP + `.agentignore`/`.cursorignore`/`.claudeignore`/`.codeiumignore` |
| **9. Git Pre-Commit Guard Installer** | [install_git_guard.py](./scripts/install_git_guard.py) | Installs `<40ms` `.git/hooks/pre-commit` secret scanner & prompt-tax bloat guard |

---

## Core Workflows

### 1. Live Quota Pool Inspection & Failover Strategy
In **Google Antigravity**, call `swarm(action="models", all=true)` and pass the JSON to `sqo_quota_pools`:
- **`HEALTHY (>50%)`**: Default complex builds to **Orchestrator (Carbon)** or **Orchestrator (Argon)**; reserve standalone **Carbon (High)** strictly for deep security/architecture.
- **`CONSERVE (20%–50%)`**: Prefer **Orchestrator (Argon)** and fan out multi-file tasks via `run_workflow(model="flash")`.
- **`CRITICAL (<20%)`**: Use **Hydrogen (`Medium` or `XHigh`)** until reset, or notify the user of untouched reserve pools (`Claude 4.6`, `GPT-OSS 120B`).
- Full matrix: [references/model-routing-matrix.md](./references/model-routing-matrix.md) & [references/parallel-workflow-patterns.md](./references/parallel-workflow-patterns.md).
