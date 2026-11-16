---
name: smart-quota-orchestrator
description: >-
  Autonomous AI Engineering OS (v13.0 Zenith Edition) with 53 native zero-dependency MCP tools, 67 CLI commands, 1-command Autopilot (sqo_autopilot), 8-gate PR Shield (sqo_pr_review), Cloud FinOps guard (sqo_finops_guard), Repo-DNA fingerprinter (sqo_repo_dna), Mermaid architecture generator (sqo_arch_diagram), evidence-backed rules compiler (sqo_compile_rules), dead-code hunter (sqo_dead_code), 4-persona council review (sqo_council_review), git forensics (sqo_git_forensics), prompt X-ray (sqo_prompt_xray), and a <15ms 3-stage token firewall.
---

# Smart Quota & Superpowers OS (`v13.0 Zenith Edition`)

Maximize engineering output per quota unit across **five active defense layers** (**53 Zero-Dependency MCP Tools** & **67 CLI Commands**):
1. **3-Stage Stateful Lifecycle Engine (`hooks.json`)**:
   - **`SessionStart`**: Auto-injects recalled architectural facts from `.sqo/memory.db` on Turn 0 (`100%` KV-cache prefix friendly).
   - **`PreToolUse`**: Blocks `>50KB` lockfile/sourcemap bombs, **deduplicates unchanged re-reads** per `conversationId`, **auto-clamps** blind full reads on `>1,200`-line source files (`overwrite: StartLine 1..280`), and **breaks 3x blind command retry loops**—automatically logging every saved token to `roi_ledger.db`!
   - **`PostToolUse`**: Maintains the `mtime_ns` file-read ledger and unlocks files immediately on `edit_file`/`write_file`.
2. **53 Native Zero-Dependency MCP Tools (`sqo-engine`)**: Including `v13.0 Zenith` flagship engines (`sqo_autopilot`, `sqo_pr_review`, `sqo_finops_guard`, `sqo_repo_dna`, `sqo_arch_diagram`, `sqo_compile_rules`, `sqo_dead_code`, `sqo_council_review`, `sqo_git_forensics`, `sqo_prompt_xray`) alongside `sqo_code_search`, `sqo_smart_outline`, `sqo_context_pack`, `sqo_blast_radius`, `sqo_memory_vault`, `sqo_dependency_slices`, `sqo_budgeted_diff`, `sqo_secret_scrub`, `sqo_quota_pools`, `sqo_benchmark`, `sqo_roi_ledger`, and more.
3. **Live `$USD` & Token ROI Ledger (`roi_ledger.py`)**: Quantifies cumulative prevented waste across Frontier (`$15/1M`), Balanced (`$3/1M`), and Fast (`$0.30/1M`) model tiers.
4. **Multi-Model & Parallel Routing (`./scripts/`)**: Pairs frontier planners (`Carbon`, `Argon`, `Opus`) with fast execution models (`Hydrogen`, `Orchestrator`, `flash` workflows).
5. **Universal 5-IDE Sync & Git Pre-Commit Guard**: Wires `sqo-engine` MCP + ignore shields across Antigravity, Cursor, Claude Code, VS Code & Windsurf, plus `<40ms` `.git/hooks/pre-commit` secret/prompt-tax protection.

---

## Bundled CLI Engines (`./scripts/`)

| Engine | Script / MCP Tool | Purpose |
| :--- | :--- | :--- |
| **1. 1-Cmd Autopilot Engine** | [autopilot_engine.py](./scripts/autopilot_engine.py) / `sqo_autopilot` | Detects framework, installs `.agentignore` + `<15ms` hook firewall, compiles rules, renders Mermaid diagram & audits security/FinOps in `<2s` |
| **2. Evidence-Backed Rules Compiler** | [compile_repo_rules.py](./scripts/compile_repo_rules.py) / `sqo_compile_rules` | Synthesizes KV-cache-safe `CLAUDE.md` / `AGENTS.md` / `.cursorrules` grounded in real AST conventions |
| **3. Live Token & `$USD` ROI Ledger** | [roi_ledger.py](./scripts/roi_ledger.py) / `sqo_roi_ledger` | Tracks cumulative tokens & `$USD` saved by autonomous hooks and compression tools |
| **4. Live Quota Pool Analyzer** | [parse_quota_pools.py](./scripts/parse_quota_pools.py) / `sqo_quota_pools` | Groups shared vs. independent reserve model pools, reset countdowns & safe `%/hr` burn ceiling |
| **5. Task Complexity & Topology Scorer** | [analyze_task_complexity.py](./scripts/analyze_task_complexity.py) | Computes Complexity (`0–100`) & Parallelizability (`0.0–1.0`) + flags security/payment/DB risks |
| **6. Monolith vs. Swarm Simulator** | [simulate_workflow_cost.py](./scripts/simulate_workflow_cost.py) | Quantifies $O(T^2)$ cumulative context burn vs `Orchestrator` & `run_workflow(model='flash')` |
| **7. Empirical Compression Benchmark** | [benchmark_suite.py](./scripts/benchmark_suite.py) / `sqo_benchmark` | Runs real measurements on the active workspace and prints verified token reduction percentages |
| **8. Session Transcript Leak Auditor** | [audit_session_burn.py](./scripts/audit_session_burn.py) | Scans Antigravity / Claude Code JSONL logs for duplicate unchanged reads & retry loops |
| **9. Interactive HTML Telemetry Center** | [generate_html_dashboard.py](./scripts/generate_html_dashboard.py) | Generates a standalone dark-glassmorphism `quota-dashboard.html` report |
| **10. Universal 5-IDE Config Synchronizer** | [sync_ide_configs.py](./scripts/sync_ide_configs.py) | Wires `sqo-engine` MCP + `.agentignore`/`.cursorignore`/`.claudeignore`/`.codeiumignore` |
| **11. Git Pre-Commit Guard Installer** | [install_git_guard.py](./scripts/install_git_guard.py) | Installs `<40ms` `.git/hooks/pre-commit` secret scanner & prompt-tax bloat guard |
| **12. Real-Time Localhost Web Center** | [live_server.py](./scripts/live_server.py) | Serves auto-refreshing Bilingual Web Command Center (`sqo serve` on `127.0.0.1:7890`) |
| **13. Smart Framework Bootstrapper** | [init_workspace_preset.py](./scripts/init_workspace_preset.py) / `sqo_init_preset` | Auto-detects Flutter/Next.js/Laravel/Python/Go/Rust & seeds ignores, MCP & memories |
| **14. Context-Rot Early-Warning Monitor** | [check_context_rot.py](./scripts/check_context_rot.py) / `sqo_context_health` | Scores quadratic session Context-Rot (`0–100`) & emits `<350`-token handoff snapshot |
| **15. Dynamic SVG Shield Badge** | [generate_repo_badge.py](./scripts/generate_repo_badge.py) / `sqo_repo_badge` | Generates embeddable GitHub SVG shield badges (`sqo badge`) with verified compression % |

---

## Core Workflows

### 1. Live Quota Pool Inspection & Failover Strategy
In **Google Antigravity**, call `swarm(action="models", all=true)` and pass the JSON to `sqo_quota_pools`:
- **`HEALTHY (>50%)`**: Default complex builds to **Orchestrator (Carbon)** or **Orchestrator (Argon)**; reserve standalone **Carbon (High)** strictly for deep security/architecture.
- **`CONSERVE (20%–50%)`**: Prefer **Orchestrator (Argon)** and fan out multi-file tasks via `run_workflow(model="flash")`.
- **`CRITICAL (<20%)`**: Use **Hydrogen (`Medium` or `XHigh`)** until reset, or notify the user of untouched reserve pools (`Claude 4.6`, `GPT-OSS 120B`).
- Full matrix: [references/model-routing-matrix.md](./references/model-routing-matrix.md) & [references/parallel-workflow-patterns.md](./references/parallel-workflow-patterns.md).
