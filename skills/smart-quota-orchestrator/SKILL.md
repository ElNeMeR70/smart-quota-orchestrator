---
name: smart-quota-orchestrator
description: >-
  Master quota-optimization & multi-agent routing skill with live quota pool
  analytics, task complexity scoring, monolith-vs-swarm quota simulation,
  session transcript leak auditing, and interactive HTML telemetry dashboards.
  Use when checking remaining model quota, choosing thinking levels (Low,
  Medium, High, XHigh), planning cost-efficient multi-agent workflows, or
  generating a visual quota & workspace health report.
---

# Smart Quota & Swarm Orchestrator (v2.0 Suite)

Maximize engineering output per quota unit by pairing **frontier reasoning models** (for architecture, security, and root-cause debugging) with **fast execution models** and **deterministic CLI pre-processors**.

## Bundled CLI Tools (`./scripts/`)

All tools run on **Python 3.8+ standard library only** (zero external dependencies):

| Tool | Script | Purpose |
| :--- | :--- | :--- |
| **1. Live Quota Pool Analyzer** | [parse_quota_pools.py](./scripts/parse_quota_pools.py) | Groups shared vs. independent model pools, calculates reset countdowns & safe `%/hr` burn rate |
| **2. Task Complexity & Topology Scorer** | [analyze_task_complexity.py](./scripts/analyze_task_complexity.py) | Computes Complexity (`0–100`) & Parallelizability (`0.0–1.0`) + flags high-risk domains |
| **3. Monolith vs. Swarm Quota Simulator** | [simulate_workflow_cost.py](./scripts/simulate_workflow_cost.py) | Quantifies cumulative quadratic token burn vs `Orchestrator` & `run_workflow(model='flash')` |
| **4. Session Transcript Leak Auditor** | [audit_session_burn.py](./scripts/audit_session_burn.py) | Scans Antigravity / Claude Code JSONL logs for duplicate file reads, error loops & bloat |
| **5. Interactive HTML Telemetry Center** | [generate_html_dashboard.py](./scripts/generate_html_dashboard.py) | Builds a standalone dark-glassmorphism `.html` report of pools, slices, tax & savings |

> **Companion Skills in This Suite:**
> - **`context-compactor`**: AST file skeletonizer (`smart_outline.py`), budgeted git diffs (`compress_git_diff.py`), test output denoiser (`compact_command_output.py`), `.agentignore` guard, and `<400-token` handoff briefs.
> - **`parallel-slice-architect`**: Import-graph partitioner (`partition_parallel_slices.py`) & auto-`run_workflow` generator.
> - **`prompt-tax-profiler`**: Audits static per-turn overhead of `AGENTS.md`, `CLAUDE.md`, `GEMINI.md`, and `SKILL.md` files.

---

## Core Workflows

### Workflow 1: Live Quota Pool Inspection & Failover Strategy
1. In **Google Antigravity**, call `swarm(action="models", all=true)` to obtain live `quota_remaining` and `quota_resets` JSON.
2. Run:
   ```bash
   python "<skill_dir>/scripts/parse_quota_pools.py" --json-string '<swarm_models_json>'
   ```
3. Route by pool health:
   - **`HEALTHY (>50%)`**: Default complex work to **Orchestrator (Carbon)** or **Orchestrator (Argon)**; reserve standalone **Carbon (High)** for security/architecture.
   - **`CONSERVE (20%–50%)`**: Use **Orchestrator (Argon)** or **Argon (Medium)**; offload batch scans to `run_workflow(model="flash")`.
   - **`CRITICAL (<20%)`**: Use **Hydrogen (`Medium` or `XHigh`)** until imminent reset, or inform the user about untouched secondary pools (`Claude 4.6`, `GPT-OSS 120B`).
   - Full model matrix: [references/model-routing-matrix.md](./references/model-routing-matrix.md).

### Workflow 2: Pre-Flight Complexity Scoring & Cost Simulation
```bash
python "<skill_dir>/scripts/analyze_task_complexity.py" --workspace . --task "<user_goal>"
python "<skill_dir>/scripts/simulate_workflow_cost.py" --files 14 --avg-loc 240 --turns 18
```
For parallel execution patterns, consult [references/parallel-workflow-patterns.md](./references/parallel-workflow-patterns.md) or activate `parallel-slice-architect`.

### Workflow 3: Visual HTML Telemetry Dashboard & Session Audit
```bash
# Audit live session transcript for redundant reads & retry loops
python "<skill_dir>/scripts/audit_session_burn.py" --auto

# Generate a standalone visual HTML report
python "<skill_dir>/scripts/generate_html_dashboard.py" --workspace . --output quota-dashboard.html
```

## Safety Invariants
- Never silently switch user-pinned models without explicit user consent or hard `0%` exhaustion.
- Enforce strict non-overlapping file ownership (`workspace="share"`) across parallel write workers.
