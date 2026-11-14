# Quota-Saving Parallel Workflow & Swarm Patterns

Copy and adapt these patterns to process 10–50x more code while keeping the main conversation context tiny and cutting frontier-model quota burn by 50–70%.

---

## Pattern 1: Cheap Map-Reduce Code Audit (`run_workflow` + `flash_lite` / `flash`)

**Why it saves quota:** Instead of reading 25 files into a heavy `Carbon` / `Opus` main session (where every subsequent turn re-pays the 25-file context tax!), fan out 25 tiny `flash_lite` workers that each read **1 file** and return a 3-line JSON finding. Only the compact summary enters your main session!

```python
# Pass to run_workflow(Script=..., Description="Parallel low-quota module audit")
phase("1. Discover target files")
targets = args.get("files", [])

phase("2. Fan-out lightweight per-file audit")
finding_schema = {
    "type": "object",
    "properties": {
        "file": {"type": "string"},
        "status": {"type": "string", "enum": ["OK", "ISSUES"]},
        "issues": {"type": "array", "items": {"type": "string"}}
    },
    "required": ["file", "status", "issues"]
}

results = await parallel(
    targets,
    lambda path: agent(
        f"Audit `{path}` strictly for security bugs, leaked secrets, and unhandled errors. "
        f"Read only `{path}`. Return concise findings.",
        schema=finding_schema,
        role=f"Audit {path}",
        model="flash"
    )
)

flagged = [r for r in results if r["status"] == "ISSUES"]
log(f"Scanned {len(targets)} files; {len(flagged)} flagged.")
print(flagged)
```

---

## Pattern 2: Staged Interface-First Parallel Build (`Stage 0 -> Parallel Stage 1 -> Verify`)

**Why it saves quota:** Prevents the #1 multi-agent quota killer — **two workers inventing incompatible types or editing the same file**, causing 5+ turns of broken-build rework.

```python
# Stage 0: Single architect defines shared contracts FIRST
phase("Stage 0: Lock shared interfaces")
contract = await agent(
    "Create `src/types/billing.ts` with strict TypeScript interfaces for Plan, Subscription, "
    "and WebhookEvent. Do not implement services yet. Return the exported type names.",
    schema={"type": "array", "items": {"type": "string"}},
    role="Contract Architect",
    model="inherit"
)

# Stage 1: Disjoint file slices in isolated shared worktrees
phase("Stage 1: Parallel slice implementation")
slices = [
    {"role": "Stripe Service", "owns": "src/services/stripe.ts", "goal": "Implement Stripe webhook & checkout helpers"},
    {"role": "Billing API", "owns": "src/routes/billing.ts", "goal": "Implement REST endpoints using src/types/billing.ts"},
    {"role": "Billing UI", "owns": "src/components/PricingTable.tsx", "goal": "Build responsive RTL-safe pricing component"},
]

summaries = await parallel(
    slices,
    lambda s: agent(
        f"You own ONLY `{s['owns']}`. Do NOT edit any other file. "
        f"Import shared contracts from `src/types/billing.ts` ({contract}). "
        f"Task: {s['goal']}. Commit your change in your workspace and return branch + diff summary.",
        schema={"type": "string"},
        role=s["role"],
        workspace="share",
        model="flash"
    )
)
for item in summaries:
    log(item)
```

---

## Pattern 3: Lean Native Swarm Rules (Zero Idle Wakeups)

Swarms are powerful but **quota-heavy** if misconfigured. Follow these five rules whenever launching `swarm`:

1. **Right-Size Worker Count**: Only spawn as many authors as there are **genuinely file-disjoint workstreams**. Four independent subsystems = 4 authors + 1 verifier (never 10 authors stepping on each other).
2. **Never Broadcast `@all` for Routine Updates**: Every `@all` wakes **every** sleeping worker and charges a full LLM turn for each one! Address the exact next peer (`@verifier check #4`), and tag `@coordinator` only when done or blocked.
3. **Reference Board Sequence Numbers (`#4`), Never Copy-Paste Logs**: Workers share the board; telling `@verifier` to check `#4` costs 5 tokens instead of pasting 2,000 tokens of test logs.
4. **Use `workspace: "share"` for Concurrent Authors**: Gives each author a lightweight git-worktree-style checkout without duplicating disk storage or colliding on uncommitted edits.
5. **Kill Finished One-Off Helpers Only After Landing Changes**: Waiting workers cost **zero tokens** while asleep, whereas `kill` permanently deletes a worker's `share`/`branch` workspace — always merge/cherry-pick first!

---

## Pattern 4: Terminal Output Filtering (Preventing Context Floods)

Never dump raw verbose CLI outputs directly into agent context:

- **Bad (burns 8,000+ tokens/turn):** `npm test` (with 500 passing verbose specs), `git log`, `cat bundle.js`
- **Good (costs <200 tokens):**
  - `npm test -- --silent` or filter only failing suites
  - `git status -sb` and `git diff --stat` before inspecting targeted hunks
  - `rg -n "pattern" src/ | head -n 40`
