# Smart Quota & Context Efficiency Guardrails

Follow these lightweight token-efficiency invariants on every turn to prevent unnecessary quota burn and context bloat:

1. **Targeted Reads Over Blind Dumps**: Search symbols or patterns first (`grep` / `ripgrep`), then read specific line ranges (`StartLine`–`EndLine`) instead of repeatedly reading entire large files (>400 lines).
2. **Never Re-Read Unchanged Files**: If a file was already read in the current conversation and has not been modified externally, rely on the existing context rather than reading it again.
3. **Break Retry Loops Early**: Never execute the same failing command more than twice without changing a concrete hypothesis, flag, or input. Inspect the error root cause before retrying.
4. **Isolate Broad Codebase Recon**: When an investigation requires reading 8+ files or exploring unfamiliar subsystems, delegate discovery to a read-only subagent so raw search noise stays out of the main conversation window.
5. **File-Disjoint Parallelism**: When fanning out work across subagents, workflows, or swarms, assign strict non-overlapping file ownership (`workspace: "share"` or `"branch"` for concurrent writers) to eliminate merge conflicts and wasted rework turns.
