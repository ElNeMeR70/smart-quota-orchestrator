---
name: apex-spec-surgeon
description: Enforces Andrej Karpathy's 4 Surgical Coding Laws, Obra/Superpowers Red-Green TDD discipline, Spec-Kit DAG task orchestration, Serena-class AST symbol editing (-85% output tokens), and Context7-class live SDK deprecation grounding. Activate whenever planning, implementing, refactoring, or reviewing non-trivial features or bug fixes.
---

# Apex Spec Surgeon (`apex-spec-surgeon` — Smart Quota OS v10.0)

You are operating with **Apex Spec Surgeon**, uniting the 6 highest-starred AI software engineering paradigms into a single zero-dependency discipline:

---

## 1. Karpathy's 4 Hard Coding Laws (Mandatory Invariants)

1. **Think & Surface Assumptions Before Coding**:
   - Never silently guess ambiguous requirements, schemas, or side effects. State assumptions explicitly or inspect contracts (`sqo_api_contracts`, `sqo_schema_distill`, `sqo_sdk_radar`) first.
2. **Simplicity First (Zero Speculative Bloat)**:
   - Write the minimum clean code that solves the exact requirement. No premature base classes, factory wrappers, or unrequested configuration layers.
3. **Surgical Scope Only (Zero Orthogonal Edits)**:
   - Touch ONLY the lines and symbols required for the task. Never reformat unrelated functions, strip helpful comments, or silently delete existing features.
   - Prefer **`sqo_edit_symbol`** over rewriting large file blocks — saving **85% of expensive Output Tokens** while guaranteeing AST/syntax validity!
4. **Goal-Driven Red-Green Verification**:
   - Never claim completion without running verification (`sqo_verify_work`, `sqo_shadow_check`, and minimal affected unit tests via `sqo_blast_radius`).

---

## 2. The 5-Stage Apex Execution Loop

### Stage A — Ground SDK Versions & Past File Gotchas (`<15ms`)
- Call **`sqo_sdk_radar`** on unfamiliar stacks so you never write deprecated syntax (e.g. Next.js 15 async `params`, Flutter `PopScope` / `.withValues()`, `google-genai`, Pydantic v2 `model_dump()`).
- Call **`sqo_memory_graph`** (`action="file_history"`) before editing complex core modules to see past bugfixes and architectural invariants.

### Stage B — Spec-Driven DAG Decomposition (For Multi-Step Features)
- Initialize a structured spec & dependency graph via **`sqo_spec_engine`** (`action="init"`), breaking work into atomic, verifiable tasks with explicit `owned_files` and `verify_cmd`.
- Pull one unblocked task at a time via `sqo_spec_engine(action="next")` (`<220 tokens`).

### Stage C — Surgical Symbol Mutation (`-85%` Output Token Burn)
- Inspect callers first with **`sqo_find_callers`** before changing any function signature.
- Mutate functions/methods directly by name with **`sqo_edit_symbol`** (`replace`, `insert_after`, `insert_before`, `delete`) — backed by automatic `Time-Machine` snapshots and `<8ms` syntax rollback protection!
- For risky architectural experiments, isolate changes inside **`sqo_worktree_sandbox`**.

### Stage D — Final 5-Gate Production Assurance (`v11.0 Hypernova`)
- Before presenting results to the user, run the 5 deterministic gates:
  1. **`sqo_verify_work`** — `0` laziness placeholders (`TODO`, `pass`, `UnimplementedError`), `0` silent feature deletions, `A+` Surgical Score.
  2. **`sqo_security_audit`** — `0` OWASP SQLi (`CWE-89`), Command Injection (`CWE-78`), XSS (`CWE-79`), or `eval` RCE sinks.
  3. **`sqo_perf_audit`** — `0` N+1 DB loops, `0` unbatched async waterfalls, `0` undisposed Flutter controllers.
  4. **`sqo_ui_audit`** — `100%` Arabic RTL directional safety (`EdgeInsetsDirectional` / `margin-inline-start`) & overflow protection.
  5. **`sqo_drift_guard`** & **`sqo_gen_tests`** — verify `.env.example` parity and synthesize unit/edge-case test suites with zero output-token waste!
