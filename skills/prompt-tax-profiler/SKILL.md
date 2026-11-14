---
name: prompt-tax-profiler
description: >-
  Audits static per-turn token overhead across AGENTS.md, CLAUDE.md, GEMINI.md,
  .cursorrules, and SKILL.md files, grades prompt architecture (A+ to D), and
  identifies bloated always-on instructions that should be refactored into
  progressive-disclosure references. Use when optimizing agent rules, creating
  skills/plugins, or diagnosing high baseline token usage.
---

# Prompt & Customization Token-Tax Profiler

Every line inside an always-on rule file (`AGENTS.md`, `CLAUDE.md`, `GEMINI.md`, `.cursorrules`) is billed on **every single conversation turn**—meaning a 3,000-token rule file quietly burns **75,000 tokens** across a 25-turn coding session!

## Workflow

1. **Run the Deterministic Token-Tax Profiler**:
   Execute [optimize_prompt_rules.py](./scripts/optimize_prompt_rules.py):
   ```bash
   python "<skill_dir>/scripts/optimize_prompt_rules.py" --workspace "<repo_path>" --turns 25
   ```
2. **Interpret the Grade & Refactor**:
   - **Grade `A+` (`<= 800` baseline tokens/turn)**: Optimal progressive disclosure.
   - **Grade `B` (`801 – 2,000` tokens/turn)**: Healthy, minor trimming optional.
   - **Grade `C/D` (`> 2,000` tokens/turn)**:
     - Keep only crisp, invariant guardrails in `AGENTS.md` / `GEMINI.md` / `CLAUDE.md`.
     - Move multi-step runbooks into `skills/<name>/SKILL.md` (where only the 30-token `name` + `description` index is loaded per turn!).
     - Move bulky API tables and code templates into `skills/<name>/references/*.md`.
