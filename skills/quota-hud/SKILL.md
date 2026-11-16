---
name: quota-hud
description: >-
  Interactive live real-time HUD and sidecar panel for monitoring quota pools,
  token burn rates, and savings ROI ledger directly in Antigravity's auxiliary side panel.
---

# Smart Quota HUD (Sidecar & Aux Pane)

Provides a live auxiliary side-panel interface for monitoring:
1. **Google Gemini Pool (Shared)**: Real-time quota percentage, countdown to refresh, and safe burn rate.
2. **Anthropic Claude Pool & OpenAI Pool**: Instant failover reserves when Gemini hits critical conservation levels.
3. **Live Token & $USD ROI Ledger**: Cumulative and daily token savings intercepted by autonomous hooks.

## Opening the Sidecar

Click the sidecar link below to open the Live HUD in Antigravity's auxiliary side pane:

👉 [Open Smart Quota HUD](sidecar://smart-quota-hud)

Or run locally in standalone browser mode via `sqo serve` or:
```bash
python sidecars/quota_hud/server.py 7899
```
