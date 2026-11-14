# Model Routing & Thinking-Level Matrix

This reference maps model families, hidden thinking-effort tiers, and quota pool behaviors across **Google Antigravity**, **Claude Code**, **Cursor**, and **Gemini CLI**.

---

## 1. Google Antigravity — Gemini 4 Ecosystem

All Gemini 4 models and Orchestrator modes draw from the **shared Gemini Quota Pool**, but their **per-turn quota consumption** varies dramatically based on parameter weight and thinking token budget:

| Model / Mode | Hidden Effort Tiers | Relative Quota Burn | Best Engineering Use Cases | Avoid Using For |
| :--- | :--- | :--- | :--- | :--- |
| **Gemini 4 Carbon** | `Low`, `Medium` *(default)*, `High` | `$$$$` (Highest) | Deep system architecture, threat modeling & Bug Bounty JS/API analysis, concurrency/race-condition debugging, novel algorithms | Boilerplate CRUD, CSS tweaks, DNS/server ops, reading 20 files sequentially |
| **Gemini 4 Argon** | `Low`, `Medium` *(default)*, `High` | `$$` (Moderate) | Daily full-stack feature development, API integrations, refactoring 3–10 files, writing comprehensive test suites | Simple formatting or one-line shell tasks |
| **Gemini 4 Hydrogen** | `Low`, `Medium` *(default)*, `High`, **`XHigh`** | `$` (Lowest) | Fast code execution, UI/Tailwind edits, CLI/MCP server ops (Hostinger, Firebase, Git), batch file updates; use **`XHigh`** when you want lightweight speed with deep step-by-step logic | Multi-service greenfield architecture from scratch |
| **Orchestrator (Carbon)** | Automatic dynamic routing | `$$` (Saves ~50–65% vs raw Carbon) | **Best flagship default.** Carbon plans architecture & resolves test failures; Hydrogen executes file searches, boilerplate edits, and build verification | Trivial 1-step questions where planning overhead isn't needed |
| **Orchestrator (Argon)** | Automatic dynamic routing | `$–$$` (Ultra-efficient) | **Best all-day coding driver.** Argon supervises design & code quality while Hydrogen handles rapid tool loops | Ultra- esoteric cryptography or zero-day vulnerability proofs (use Carbon High) |
| **Gemini 3.8 Flash** | `Low`, `Medium`, `High` | `$` (Low) | Browser subagent automation (`Model="flash"`), high-volume parallel `run_workflow` workers | Complex cross-module architectural refactors |

---

## 2. Secondary Independent Quota Pools (Failover Reserves)

In multi-provider environments like Antigravity and Cursor, non-Gemini models often sit on **independent quota counters and separate reset timers**:

| Model | Pool Behavior | Ideal Role in Multi-Pool Strategy |
| :--- | :--- | :--- |
| **Claude Opus 4.6 (Thinking)** | Separate non-Gemini pool | Reserve for second-opinion security/architecture reviews or failover when Gemini pool drops below `15%` before reset |
| **Claude Sonnet 4.6 (Thinking)** | Separate non-Gemini pool | High-speed full-stack coding & clean frontend UI generation during Gemini pool cooldowns |
| **GPT-OSS 120B (Medium)** | Separate open-weights pool | Great zero-stress reserve for documentation, data transformations, SQL queries, and routine unit test generation |

---

## 3. Thinking-Level Selection Cheat Sheet (`Low` vs `Medium` vs `High` vs `XHigh`)

Thinking tokens are billed against your quota **even though they don't appear in final code diffs**:

1. **`Low`**:
   - Cuts internal reasoning tokens by ~60–75%.
   - Use for: Renaming symbols, updating `.env.example`, running deployment checklists, MCP tool operations, translating UI strings.
2. **`Medium` (Recommended Default)**:
   - Balanced reasoning depth for 80% of software engineering tasks.
3. **`High`**:
   - Multiplies hypothesis generation and edge-case verification loops.
   - Use for: Auth/RBAC security rules, payment webhooks, intermittent async bugs, database schema migrations.
4. **`XHigh` (Hydrogen Exclusive Secret Weapon)**:
   - Pairs Hydrogen's fast, low-cost weights with an extended reasoning chain — ideal for tricky algorithmic puzzles or large file transformations when conserving quota.

---

## 4. Subagent & Workflow Tier Mapping (`run_workflow` / `invoke_subagent`)

When spawning programmatic child agents in Antigravity's `run_workflow` or `invoke_subagent`:

- **`model="flash_lite"`**: Log parsing, extracting endpoints/exports from 20+ files, docstrings, lint fixes, translation keys.
- **`model="flash"`**: Default for `browser` subagent, per-file code reviews, unit test generation per module, isolated bug reproduction.
- **`model="inherit"`**: Default when the user chose a specific model for cohesive code authoring or `swarm` workers.
