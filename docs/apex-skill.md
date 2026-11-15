# ⚡ Apex Spec Surgeon + Karpathy + FinOps + Quota Guard (`CLAUDE.md` / `AGENTS.md` / `SKILL.md`)
> Powered by **Smart Quota & Superpowers OS v12.0 Quantum** — https://sqo.elnemer-ai.com
> Drop this file into any repository as `CLAUDE.md`, `AGENTS.md`, or `.agent/skills/apex/SKILL.md` — or install the full 48-tool MCP engine via `npx -y smart-quota-orchestrator init --workspace .`

## 1. Andrej Karpathy's 4 Surgical Laws
1. **Surface Assumptions First:** Never guess ambiguous schemas, auth flows, or side effects silently. Inspect contracts (`sqo_repo_dna`, `sqo_api_contracts`, `sqo_git_forensics`) or state assumptions explicitly before coding.
2. **Simplicity Over Speculation:** Write the minimal, direct code that solves the exact prompt. No unrequested abstractions, wrapper classes, or premature config layers.
3. **Surgical Scope Only:** Modify ONLY the exact functions and files required. Never reformat orthogonal code, strip helpful comments, or silently delete existing features.
4. **Goal-Driven Red-Green Verification:** Define verifiable success criteria first; never leave `TODO` stubs, `pass` placeholders, or `UnimplementedError` traps.

## 2. Token & Quota Efficiency Invariants (-96.8% Input / -85% Output Waste)
1. **Targeted Reads Over Blind Dumps:** Use `sqo_repo_dna` (`<420` tokens) or `sqo_code_search` first, then read bounded line windows (`StartLine`–`EndLine`) rather than dumping >500-line files or lockfiles (`package-lock.json`, `pubspec.lock`, `*.min.js`).
2. **Zero Duplicate Reads:** Never re-read a file already in your conversation context unless it changed on disk.
3. **Break Retry Loops Early:** Never run an identical failing terminal command 3× in a row without changing code, flags, or inputs.
4. **Symbol-Level Output Economy:** Edit targeted functions (`sqo_edit_symbol`) instead of rewriting entire files from scratch.

## 3. Production, Security & FinOps Hard Gates (Zero Wallet-Shock / Zero 3 AM Pages)
1. **Cloud & AI Wallet Protection (`sqo_finops_guard`):** Never place Firestore `onSnapshot`/`fetch` inside React `useEffect` without a `[]` dependency array; never write back to the same collection inside `onDocumentWritten` without an idempotency guard; always set `max_tokens`/`max_output_tokens` on LLM calls and never invoke paid LLMs inside unbatched loops.
2. **Adversarial Reliability (`sqo_council_review` & `sqo_security_audit`):** Use parameterized SQL bindings (`?`), atomic SQL updates for wallet/balance deductions (no TOCTOU race conditions), explicit `timeout=` on all HTTP requests, and directional CSS/Flutter properties (`margin-inline-start`, `EdgeInsetsDirectional`) for Arabic RTL parity.
