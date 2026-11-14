---
name: prompt-tax-profiler
description: >-
  Audits static per-turn token overhead across AGENTS.md, CLAUDE.md, GEMINI.md,
  .cursorrules, and SKILL.md files, grades prompt architecture (A+ to D), and
  verifies LLM Prompt KV-Cache prefix stability (90% cached-token discount
  protection). Use when optimizing agent rules, hooks, plugins, or diagnosing
  high baseline token usage and KV-cache invalidation.
---

# Prompt Token-Tax & KV-Cache Stability Profiler (`v4.0`)

Every line inside an always-on rule file (`AGENTS.md`, `CLAUDE.md`, `GEMINI.md`, `.cursorrules`) is billed on **every single conversation turn**, AND any volatile dynamic injection (`datetime.now()`, `uuid4()`, unsorted `os.listdir()`, or `PreInvocation` message mutation) destroys the **90% LLM Prompt KV-Cache discount** across the entire conversation prefix!

## Bundled Engines (`./scripts/`)

| Engine | Script | Native MCP Tool | Purpose |
| :--- | :--- | :--- | :--- |
| **1. Static Prompt-Tax Profiler** | [optimize_prompt_rules.py](./scripts/optimize_prompt_rules.py) | CLI / `sqo tax` | Measures always-on rule overhead vs progressive-disclosure skills and grades `A+` to `D` |
| **2. KV-Cache Prefix Stability Auditor** | [audit_cache_stability.py](./scripts/audit_cache_stability.py) | `sqo_cache_audit` | Detects `PreInvocation` cache-busting hooks, volatile timestamps/UUIDs in `injectSteps`, and non-deterministic directory walks (`0–100` score) |

---

## Workflow

1. **Measure Always-On Rule Overhead**:
   ```bash
   python "<skill_dir>/scripts/optimize_prompt_rules.py" --workspace "<repo_path>" --turns 25
   ```
2. **Verify 90% Prompt KV-Cache Prefix Stability**:
   ```bash
   python "<skill_dir>/scripts/audit_cache_stability.py" --workspace "<repo_path>"
   ```
3. **Refactor When Needed**:
   - Keep `AGENTS.md` / `GEMINI.md` / `CLAUDE.md` crisp (`<= 800` tokens/turn -> Grade **`A+`**).
   - Inject recalled workspace context once at **`SessionStart`** (never via volatile per-turn `PreInvocation` timestamps).
   - Move multi-step runbooks into `skills/<name>/SKILL.md` and bulky tables into `skills/<name>/references/*.md`.
