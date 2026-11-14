---
name: smart-quota-orchestrator
description: >-
  Autonomous AI quota & multi-agent orchestration engine with 10 native MCP
  tools, real-time PreToolUse token-bomb shield, live quota pool analytics,
  task complexity scoring, monolith-vs-swarm cost simulation, empirical
  compression benchmarks, session burn auditing, and interactive HTML telemetry
  dashboards. Use when checking or optimizing model quota, choosing thinking
  levels, benchmarking workspace token savings, or orchestrating parallel agents.
---

# Smart Quota & Swarm Orchestrator (`v3.0` Autonomous Suite)

Maximize engineering output per quota unit across **three active defense layers**:
1. **Autonomous Runtime Shield (`hooks.json`)**: Intercepts accidental `read_file` / `cat` dumps on giant lockfiles, sourcemaps, and minified bundles in `<15ms` before tokens are billed.
2. **Native Zero-Dependency MCP Engine (`sqo-engine`)**: Exposes 10 structured tools (`sqo_code_search`, `sqo_smart_outline`, `sqo_context_pack`, `sqo_blast_radius`, `sqo_memory_vault`, `sqo_dependency_slices`, `sqo_budgeted_diff`, `sqo_secret_scrub`, `sqo_quota_pools`, `sqo_benchmark`).
3. **Multi-Model & Parallel Routing (`./scripts/`)**: Pairs frontier planners (`Carbon`, `Argon`, `Opus`) with fast execution models (`Hydrogen`, `Orchestrator`, `flash` workflows).

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

---

## Core Workflows

### 1. Live Quota Pool Inspection & Failover Strategy
In **Google Antigravity**, call `swarm(action="models", all=true)` and pass the JSON to `sqo_quota_pools` (or `parse_quota_pools.py`):
- **`HEALTHY (>50%)`**: Default complex builds to **Orchestrator (Carbon)** or **Orchestrator (Argon)**; reserve standalone **Carbon (High)** strictly for deep security/architecture.
- **`CONSERVE (20%–50%)`**: Prefer **Orchestrator (Argon)** and fan out multi-file tasks via `run_workflow(model="flash")`.
- **`CRITICAL (<20%)`**: Use **Hydrogen (`Medium` or `XHigh`)** until reset, or notify the user of untouched reserve pools (`Claude 4.6`, `GPT-OSS 120B`).
- Full matrix: [references/model-routing-matrix.md](./references/model-routing-matrix.md).

### 2. Empirical Benchmark & Workspace Doctor
```bash
# Run live Before-vs-After token compression benchmark on the current repo
python "<skill_dir>/scripts/benchmark_suite.py" --workspace .

# Generate visual HTML telemetry dashboard
python "<skill_dir>/scripts/generate_html_dashboard.py" --workspace . --output quota-dashboard.html
```
For parallel `run_workflow` & `swarm` templates, read [references/parallel-workflow-patterns.md](./references/parallel-workflow-patterns.md).
