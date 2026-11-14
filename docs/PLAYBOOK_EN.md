# 📘 Smart Quota & Swarm Orchestrator v5.0 — Engineering Playbook (English)

[⬅️ Back to Main README](../README.md) • [🇸🇦 قراءة الدليل العملي بالعربية](./PLAYBOOK_AR.md)

This playbook provides **copy-paste workflows, real-world agent dialogues, and team blueprints** for getting 10x–25x more engineering output from every AI quota window across **Google Antigravity, Claude Code, Cursor, VS Code, Gemini CLI, and Windsurf**.

---

## 🎭 Part 1: 4 Real-World Agent Dialogues (Before vs. After)

### Dialogue 1: Production Payment Crash at 2:00 AM
> **Developer Prompt:** *"Users are getting a 500 error on `/api/v1/stripe/webhook`. Here is the 45-line stack trace from Sentry—fix it fast!"*

#### ❌ Without Smart Quota OS (Naive Agent)
1. **Turn 1**: Agent runs `grep -rn "webhook" .` -> dumps 180 matches (`6,400` tokens).
2. **Turn 2**: Agent reads all of `src/server.ts` (`1,450` lines -> `14,200` tokens).
3. **Turn 3**: Agent reads all of `src/billing/stripe.ts` (`980` lines -> `9,600` tokens).
4. **Turn 4**: Agent accidentally reads `dist/server.js.map` (`68,000` tokens!!).
5. **Turn 5**: Agent edits `stripe.ts`, runs `npm test` (all 210 test suites -> `11,500` tokens of noisy logs).
- **Total Cost**: **5 turns • `109,700` tokens burned (`~38%` of 5-hour frontier quota!)**

#### ✅ With Smart Quota & Swarm Orchestrator `v5.0`
1. **Turn 0 (`SessionStart` Hook)**: Automatically injects stored memory:
   `[arch] Stripe webhook requires raw Buffer before express.json() middleware (src/server.ts:L42)`.
2. **Turn 1**: Agent calls native MCP tool **`sqo_pinpoint_error(stack_trace=...)`**:
   - Skips all `node_modules` frames automatically.
   - Extracts exact `±10` line windows around `src/billing/stripe.ts:L114` and `src/server.ts:L42` (`580` tokens total!).
3. **Turn 2**: Agent applies surgical `edit_file`, calls **`sqo_blast_radius(["src/billing/stripe.ts"])`** -> discovers **only** `tests/stripe_webhook.spec.ts` is affected, and runs it via `sqo denoise` (`95` tokens!).
- **Total Cost**: **2 turns • `1,120` tokens (`98.9%` savings — `<1%` quota used!)**

---

### Dialogue 2: Large Multi-File SaaS Feature (18 Files Across Backend + UI)
> **Developer Prompt:** *"Add multi-workspace RBAC roles (`owner`, `admin`, `viewer`) across our Prisma schema, API routes, and React dashboard."*

#### ❌ Without Smart Quota OS
- Single frontier agent (`Carbon High` or `Claude Opus`) edits 18 files sequentially over 24 turns.
- Because conversation history grows quadratically ($O(T^2)$), Turn 20 re-bills 140,000 tokens of prior diffs and file reads—hitting the quota wall mid-feature!

#### ✅ With Smart Quota OS `v5.0`
1. **Planner Step**: Agent runs **`sqo_dependency_slices(workspace=".", max_workers=4, emit_workflow=True)`**:
   - **Stage 0 (Sequential Shared Contracts)**: `prisma/schema.prisma` & `src/types/rbac.ts` (`imported_by >= 3` modules) are edited **first** by the lead planner so types are locked!
   - **Stage 1 (4 Collision-Free Parallel Slices)**:
     - `slice-1`: Backend Middleware & Guards (`src/middleware/*`)
     - `slice-2`: Billing & Team Endpoints (`src/routes/team/*`)
     - `slice-3`: Dashboard Settings UI (`src/components/team/*`)
     - `slice-4`: RBAC Unit & Integration Tests (`tests/rbac/*`)
2. **Execution**: Dispatched in parallel to fast `flash` / `Hydrogen` workers with **zero merge conflicts**!
- **Result**: Completed in **3.5 minutes** with **81% less frontier quota burn**!

---

## 🛠️ Part 2: Role-Based Workflows

### 1. For Solo Indie Hackers & SaaS Builders
Run these 3 commands once on every new repo:
```bash
# 1. Wire MCP + ignore shields across Cursor, Antigravity, Claude Code & VS Code
python sqo.py sync-ide --workspace . --ides all

# 2. Install the <40ms Git pre-commit secret & prompt-bloat shield
python sqo.py git-guard --workspace .

# 3. Map every API endpoint & UI page + save core architecture facts
python sqo.py routes --workspace .
python sqo.py memory --workspace . remember --category arch --title "Auth & Billing" --detail "JWT in HttpOnly cookie; Stripe webhooks at /api/webhooks/stripe"
```

### 2. For Mobile (Flutter / React Native) & Frontend Engineers
UI repositories often contain high-res 4K PNG mockups, `.arb`/JSON translations, and `pubspec.lock`/`Podfile.lock` bombs:
```bash
# Audit PNG/JPEG/WebP/PDF vision tile costs BEFORE attaching assets to prompts!
python sqo.py media --workspace assets/

# Map all Flutter GoRouter / MaterialApp routes + complexity hotspots
python sqo.py routes --workspace .
python sqo.py hotspots --workspace lib/
```

### 3. For Tech Leads & Monorepo Architects
Check your team's prompt hygiene and cumulative dollar savings weekly:
```bash
# Full 8-in-1 health check (ROI + Prompt Tax + KV-Cache + Secrets + Benchmarks)
python sqo.py doctor --workspace .

# Generate a shareable dark-glassmorphism HTML report for your team
python sqo.py dashboard --workspace . --output quota-dashboard.html
```
