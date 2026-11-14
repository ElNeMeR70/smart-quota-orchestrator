---
name: context-compactor
description: >-
  Eliminates context bloat with 5 deterministic CLI tools: AST/symbol file
  skeletonizer (read 2,000-line files in <120 tokens), token-budgeted git diff
  compressor, build/test CLI output denoiser, context-bomb .agentignore
  generator, and <400-token zero-loss handoff brief builder for /compact and
  subagents. Use when reading large files, reviewing big diffs, running noisy
  tests, shielding repos from token bombs, or compacting long sessions.
---

# Context Compactor & High-Signal Compression Toolkit

Prevent prompt bloat **before** it enters the conversation window using five zero-dependency Python CLI utilities located in `./scripts/`:

| Tool | Script | Typical Token Savings | When to Use |
| :--- | :--- | :--- | :--- |
| **1. Structural File Skeletonizer** | [smart_outline.py](./scripts/smart_outline.py) | **85% – 96%** | Before reading any file `> 300` lines — inspect symbol signatures + `Lstart-Lend` ranges first! |
| **2. Token-Budgeted Git Diff** | [compress_git_diff.py](./scripts/compress_git_diff.py) | **70% – 95%** | Reviewing working-tree or branch diffs without lockfile/bundle/SVG token floods |
| **3. CLI Test/Build Denoiser** | [compact_command_output.py](./scripts/compact_command_output.py) | **80% – 95%** | Running `pytest`, `vitest`, `jest`, `npm test`, `tsc`, `flutter test`, or verbose builds |
| **4. Context-Bomb Ignore Guard** | [generate_agent_ignore.py](./scripts/generate_agent_ignore.py) | **Prevents 10k–200k accidents** | Scanning repos for heavy dumps/sourcemaps and generating `.agentignore` / `.cursorignore` |
| **5. Zero-Loss Handoff Brief** | [build_handoff_brief.py](./scripts/build_handoff_brief.py) | **90%+ on resume** | Packaging branch, dirty files, and next atomic actions (<400 tokens) before `/compact` or subagent handoff |

---

## Usage Recipes

### 1. Inspect Large Files Without Reading the Whole File
```bash
# Get every class/function signature + exact line numbers
python "<skill_dir>/scripts/smart_outline.py" path/to/large_file.ts

# Extract ONLY one target symbol's body with line numbers
python "<skill_dir>/scripts/smart_outline.py" path/to/large_file.ts --symbol handleWebhook
```

### 2. Review Git Diffs Inside a Strict Token Budget
```bash
python "<skill_dir>/scripts/compress_git_diff.py" --workspace . --max-tokens 1800
```

### 3. Run Noisy Test Suites & Keep Only Actionable Failures
```bash
python "<skill_dir>/scripts/compact_command_output.py" --cmd "npm test"
```

### 4. Shield Workspace from Context-Poisoning Files
```bash
# Scan & write .agentignore (or pass --target .cursorignore / .claudeignore)
python "<skill_dir>/scripts/generate_agent_ignore.py" --workspace . --write
```

### 5. Build a `<400-Token` Handoff Snapshot Before `/compact`
```bash
python "<skill_dir>/scripts/build_handoff_brief.py" \
  --workspace . \
  --goal "Complete billing webhook handler" \
  --next "Add signature unit test" "Verify staging build"
```
