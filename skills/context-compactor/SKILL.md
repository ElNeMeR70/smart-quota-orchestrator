---
name: context-compactor
description: >-
  Generates ultra-compact (<400 token) deterministic state & git handoff briefs
  so long conversations can be compacted (/compact), switched across models, or
  delegated to fresh subagents and swarm workers with zero context loss and
  minimal token overhead. Use when conversations grow long, before switching
  models, or when briefing subagents/swarm workers.
---

# Context Compactor & Zero-Loss Handoff Builder

Long agent sessions silently multiply quota consumption because **every new turn re-sends the accumulated conversation history**. This skill packages the exact state of work into a tiny, deterministic Markdown brief (<400 tokens) so `/compact`, model switches, or fresh subagent handoffs start warm without re-exploring the codebase.

## Workflow

1. **Generate the Deterministic Workspace Snapshot**:
   Run [build_handoff_brief.py](./scripts/build_handoff_brief.py):
   ```bash
   python "<skill_dir>/scripts/build_handoff_brief.py" --workspace "<repo_path>" --goal "<current_objective>" --next "<remaining_steps>"
   ```
2. **Choose the Right Continuation Path**:
   - **Continuing in the Same Chat**: Present the generated brief and recommend the `/compact` slash command to free up the context window immediately.
   - **Delegating to a Subagent or Swarm Worker**: Paste the compact brief directly into `invoke_subagent(Prompt=...)` or `swarm(action="add", brief=...)` so the worker knows the exact modified files, git branch, and remaining checklist on Turn 1 without wasting 10 discovery turns.
   - **Switching to a Reserve Model Pool**: Save the brief to `HANDOFF.md` (only if requested by the user) or keep it in the last turn before switching models.
