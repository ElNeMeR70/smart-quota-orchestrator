---
name: context-compactor
description: >-
  Eliminates context bloat with 6 deterministic CLI tools: AST/symbol file
  skeletonizer, adaptive Repomix-style multi-file context packer, token-budgeted
  git diff compressor, build/test CLI output denoiser, context-bomb .agentignore
  generator, and <400-token zero-loss handoff brief builder. Use when reading
  large files, packing multi-file context, reviewing big diffs, running noisy
  tests, or compacting long sessions.
---

# Context Compactor & Adaptive Compression Toolkit (`v3.0`)

Prevent prompt bloat **before** it enters the conversation window using six zero-dependency Python CLI utilities (and native `sqo-engine` MCP tools):

| Tool | Script / MCP Tool | Typical Token Savings | When to Use |
| :--- | :--- | :--- | :--- |
| **1. Structural File Skeletonizer** | [smart_outline.py](./scripts/smart_outline.py) / `sqo_smart_outline` | **85% – 96%** | Before reading any file `> 250` lines — inspect symbol signatures + `Lstart-Lend` ranges first |
| **2. Adaptive Multi-File Context Packer** | [pack_context_bundle.py](./scripts/pack_context_bundle.py) / `sqo_context_pack` | **75% – 92%** | Pack 20–100 files into an exact `--max-tokens` budget (Full focus files + AST skeletons + index) |
| **3. Token-Budgeted Git Diff** | [compress_git_diff.py](./scripts/compress_git_diff.py) / `sqo_budgeted_diff` | **70% – 95%** | Review working-tree or branch diffs without lockfile/bundle/SVG token floods |
| **4. CLI Test/Build Denoiser** | [compact_command_output.py](./scripts/compact_command_output.py) | **80% – 95%** | Run `pytest`, `vitest`, `jest`, `npm test`, `tsc`, or `flutter test` cleanly |
| **5. Context-Bomb Ignore Guard** | [generate_agent_ignore.py](./scripts/generate_agent_ignore.py) | **Prevents 10k–200k accidents** | Scan repos for heavy dumps/sourcemaps and write `.agentignore` / `.cursorignore` |
| **6. Zero-Loss Handoff Brief** | [build_handoff_brief.py](./scripts/build_handoff_brief.py) | **90%+ on resume** | Package branch, dirty files, and next atomic actions (`<400` tokens) before `/compact` or subagents |

---

## Quick Usage

```bash
# 1. Outline a large file or extract a single method
python "<skill_dir>/scripts/smart_outline.py" path/to/large_file.ts
python "<skill_dir>/scripts/smart_outline.py" path/to/large_file.ts --symbol handleWebhook

# 2. Pack an entire subsystem into <= 3,000 tokens
python "<skill_dir>/scripts/pack_context_bundle.py" --workspace . --paths src/billing --focus stripe.ts --max-tokens 3000

# 3. Compress git diff & denoise test runners
python "<skill_dir>/scripts/compress_git_diff.py" --workspace . --max-tokens 1800
python "<skill_dir>/scripts/compact_command_output.py" --cmd "npm test"
```
