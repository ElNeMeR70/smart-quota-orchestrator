---
name: parallel-slice-architect
description: >-
  Parses real Python, TypeScript/JS, Dart, Go, and PHP import dependency graphs
  to partition any codebase into Stage-0 Shared Contracts and Stage-1
  collision-free parallel worker slices, and auto-generates Antigravity
  run_workflow scripts. Use before launching parallel subagents, workflows, or
  swarms to guarantee zero merge conflicts.
---

# Parallel Slice Architect (Dependency-Safe Multi-Agent Partitioner)

Concurrent write agents fail and waste massive quota whenever two workers edit the same file or invent incompatible interfaces. This skill inspects the **actual import graph** of a workspace and partitions work into guaranteed **file-disjoint slices**.

## Commands

Run [partition_parallel_slices.py](./scripts/partition_parallel_slices.py):

```bash
# 1. Inspect Stage-0 shared foundations & Stage-1 disjoint worker buckets
python "<skill_dir>/scripts/partition_parallel_slices.py" --workspace "<repo_path>" --max-workers 4

# 2. Emit a ready-to-execute Antigravity run_workflow Python script!
python "<skill_dir>/scripts/partition_parallel_slices.py" \
  --workspace "<repo_path>" \
  --max-workers 4 \
  --goal "<feature_or_refactor_goal>" \
  --emit-workflow
```

## Execution Protocol

1. **Stage 0 (Sequential Lock)**: Files with high local fan-in (`imported_by_count >= 2`) or files in `types/` / `schemas/` / `contracts/` are locked and updated **first** by a single architect turn.
2. **Stage 1 (Parallel Fan-Out)**: Connected components among remaining files are balanced into `1..N` strictly non-overlapping worker buckets. Pass `workspace="share"` when running concurrent write agents so each worker commits cleanly in an isolated checkout.
3. **Stage 2 (Verification)**: Run a single denoised verification command (`compact_command_output.py --cmd "<test_command>"`) after merging slices.
