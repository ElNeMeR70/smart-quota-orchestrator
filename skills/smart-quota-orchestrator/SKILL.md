---
name: smart-quota-orchestrator
description: >-
  Inspects live AI model quota pools, classifies task complexity, audits session
  token leaks, and routes work across fast execution models, subagents, dynamic
  workflows, and parallel swarms to cut quota burn by 50-70%. Use when the user
  asks to check or optimize model quota, choose the best model/thinking level,
  plan a large task efficiently, audit why tokens are draining fast, or run
  cost-efficient multi-agent workflows.
---

# Smart Quota & Swarm Orchestrator

Maximize engineering throughput per quota unit by pairing **frontier reasoning models** (for architecture, security, and hard debugging) with **fast execution tiers** (for file discovery, mechanical edits, test runs, and high-fan-out tasks).

## Quick Command Reference (Bundled CLI Tools)

All helper scripts use **Python 3.8+ standard library only** (zero `pip` dependencies, cross-platform Windows/macOS/Linux):

| Goal | Command |
| :--- | :--- |
| **1. Parse Live Quota Pools & Reset Timers** | `python scripts/parse_quota_pools.py --input <models_json_file>` |
| **2. Score Task Complexity & Parallel Split** | `python scripts/analyze_task_complexity.py --workspace . --task "<goal>"` |
| **3. Audit Session Transcript for Token Leaks** | `python scripts/audit_session_burn.py --auto` |

*(Resolve `scripts/...` relative to this `SKILL.md` directory.)*

---

## Workflow 1: Live Quota Pool Inspection & Failover Strategy

When the user asks about remaining quota, reset times, which model to pick, or how to stretch their current allowance:

1. **Fetch Live Model & Quota Telemetry**:
   - **In Google Antigravity**: Call `swarm(action="models", all=true)` to retrieve real-time `quota_remaining`, `quota_resets`, and `display_names` across every model pool.
   - **In Claude Code / Cursor / Gemini CLI**: Inspect active model tier settings or pass `--preset` to `parse_quota_pools.py`.
2. **Analyze Shared vs. Independent Quota Pools**:
   - Pipe or pass the JSON output to [parse_quota_pools.py](./scripts/parse_quota_pools.py):
     ```bash
     python "<skill_dir>/scripts/parse_quota_pools.py" --json-string '<swarm_models_json>'
     ```
   - Understand **Shared Pool Coupling**:
     - All **Gemini** variants (`Gemini 4 Carbon`, `Argon`, `Hydrogen`, `Orchestrator`, and `Gemini 3.8 Flash`) draw from the **same shared Gemini pool** — though lighter tiers (`Hydrogen`, `Argon`, `Orchestrator`) burn **significantly less quota per task** than standalone `Carbon`.
     - **Non-Gemini Frontier Pools** (such as `Claude Opus 4.6`, `Claude Sonnet 4.6`, and `GPT-OSS 120B`) operate on **separate quota pools and reset clocks**, serving as zero-downtime failover reserves when the primary pool drops below `20%`.
3. **Apply Pool-Health Routing Rules**:
   - **Healthy (`> 50%` remaining)**: Prefer **Orchestrator (Carbon)** or **Orchestrator (Argon)** for complex builds; reserve standalone **Carbon (High)** strictly for security audits, deep debugging, and architecture design.
   - **Conserve (`20% – 50%` remaining)**: Default interactive work to **Orchestrator (Argon)** or **Argon (Medium)**; offload batch/repetitive work via `run_workflow` using `model="flash"` or `model="flash_lite"`.
   - **Critical (`< 20%` remaining)**:
     - Check `time_until_reset`: if reset is **< 30 minutes away**, use `Hydrogen (Medium)` or `flash` for urgent fixes until the pool refreshes.
     - If reset is **hours away** and heavy reasoning is needed, recommend switching to an untouched secondary pool (e.g., `Claude Sonnet 4.6` / `Opus 4.6`) **only with user confirmation** (never silently switch user-pinned models on your own).

For complete model-by-model characteristics and thinking-level guidance (`Low`, `Medium`, `High`, `XHigh`), read [references/model-routing-matrix.md](./references/model-routing-matrix.md).

---

## Workflow 2: Pre-Flight Complexity Scoring & Execution Routing

Before launching a multi-file feature, refactor, or codebase-wide task, run the deterministic analyzer:

```bash
python "<skill_dir>/scripts/analyze_task_complexity.py" --workspace "<repo_path>" --task "<user_request>"
```

Use its **Complexity Score (`0–100`)** and **Parallelizability Index (`0.0–1.0`)** to pick the leanest execution topology:

| Score | Parallelizability | Optimal Execution Topology | Target Model Tier |
| :--- | :--- | :--- | :--- |
| **`0 – 25`** (Trivial / Localized) | Any | **Direct Inline Execution** (no subagents; subagent startup overhead costs more than doing it inline) | Current model (`Low`/`Medium`) or `Hydrogen` |
| **`26 – 55`** (Moderate / 3–8 files) | `< 0.5` | **Single-Agent Staged Edit** (grep -> targeted line reads -> edit -> single test run) | `Argon (Medium)` or `Orchestrator (Argon)` |
| **`26 – 65`** (Broad Recon / Batch) | `>= 0.5` | **`run_workflow` Parallel Fan-Out** over independent files/modules with `model="flash"` or `"flash_lite"` | Planner: current model; Workers: `flash` / `flash_lite` |
| **`66 – 100`** (Complex / High-Risk) | `< 0.5` | **Read-Only Recon Subagent** (`research` or `quota-planner`) -> Main Agent Deep Implementation | `Orchestrator (Carbon)` or `Carbon (High)` |
| **`66 – 100`** (Large Multi-Subsystem) | `>= 0.5` | **Isolated Worktree Pipeline / Swarm** (`workspace="share"`, strict file ownership + 1 Verifier per 3 Authors) | User's chosen model (or `Orchestrator`) |

For ready-to-run `run_workflow` and `swarm` templates, read [references/parallel-workflow-patterns.md](./references/parallel-workflow-patterns.md).

---

## Workflow 3: Auditing Session Token Leaks & Bloat

When a conversation feels sluggish, quota drops faster than expected, or the user asks *"why did my quota drain so fast?"*:

1. Run [audit_session_burn.py](./scripts/audit_session_burn.py):
   ```bash
   python "<skill_dir>/scripts/audit_session_burn.py" --auto
   ```
   *(Or pass `--transcript "<path_to_transcript.jsonl>"` directly.)*
2. Review the detected **Token Leak Signatures**:
   - **Redundant Full-File Reads**: Same file read multiple times without intermediate edits.
   - **Unbounded Command Output Floods**: Commands dumping thousands of lines (`cat`, unfiltered `git diff`, verbose build logs) into the prompt history.
   - **Error Thrashing Loops**: 3+ consecutive failed tool invocations on the same target.
   - **Cumulative Context Weight**: Total steps and payload size carried on every subsequent turn.
3. **Remediate Immediately**:
   - If the audit flags **`HIGH BLOAT`**, pair with the `context-compactor` skill (`build_handoff_brief.py`) to generate a <400-token state summary and recommend the `/compact` command (or start a clean subagent with that brief).

---

## Verification & Safety Invariants

- **Never Auto-Switch Models Silently**: Respect user model pins. Only switch a swarm worker's model on actual quota exhaustion (`0%`) or explicit user instruction, and always state why.
- **Zero Collisions in Parallel Runs**: Never assign two concurrent write agents to the same file. Define shared schemas/interfaces in Stage 0 before parallelizing Stage 1.
- **Verify Script Output**: Always inspect exit codes (`0` = success) and JSON/table metrics from `scripts/*.py` before presenting quota percentages or reset countdowns to the user.
