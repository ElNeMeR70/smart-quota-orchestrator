---
name: project-memory-vault
description: >-
  Persistent cross-session SQLite FTS5 architectural memory bank and 10-pattern
  secret/PII redactor. Use to store and recall project architecture decisions,
  tricky gotchas, and key file maps across sessions so new conversations skip
  costly codebase re-discovery, and to audit or scrub secrets safely.
---

# Project Memory Vault & Zero-Leak Secret Guard

Every fresh chat normally wastes 10–20 turns re-discovering the same architectural conventions. **Project Memory Vault** persists compact project facts in a local SQLite FTS5 database (`.sqo/memory.db` or `$PLUGIN_DATA`) and recalls them via BM25 in `<15ms`.

## Bundled Engines (`./scripts/`)

| Engine | Script | Purpose |
| :--- | :--- | :--- |
| **1. Architectural Memory Vault** | [memory_vault.py](./scripts/memory_vault.py) | `remember`, `recall`, `list`, and `forget` persistent project facts indexed with SQLite FTS5 |
| **2. Zero-Leak Secret Guard** | [scrub_secrets.py](./scripts/scrub_secrets.py) | Scans repos for hardcoded API keys/PATs/JWTs/DB URIs (masked output only) or scrubs snippets before prompt ingestion |

---

## Workflows

### 1. Recall Architectural Context at the Start of a Task
```bash
python "<skill_dir>/scripts/memory_vault.py" --workspace . recall "authentication webhook database"
```
*(Or call the native MCP tool `sqo_memory_vault` with `action="recall"`.)*

### 2. Persist Non-Obvious Discoveries & Gotchas for Future Sessions
Whenever you solve a subtle bug, map a complex subsystem, or establish an architectural invariant:
```bash
python "<skill_dir>/scripts/memory_vault.py" --workspace . remember \
  --category "auth" \
  --title "Webhook signature verification" \
  --detail "Raw body buffer is required before JSON middleware in src/server.ts:L42" \
  --files src/server.ts src/webhooks/stripe.ts
```

### 3. Audit Hardcoded Secrets Safely (Zero Raw Values Printed)
```bash
python "<skill_dir>/scripts/scrub_secrets.py" --scan-workspace .
```
