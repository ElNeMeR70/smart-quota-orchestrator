#!/usr/bin/env bash
set -euo pipefail

REPO_URL="https://github.com/ElNeMeR70/smart-quota-orchestrator.git"
AGY_PLUGIN_DIR="${HOME}/.gemini/config/plugins/smart-quota-orchestrator"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

echo "==> Installing Smart Quota & Swarm Orchestrator v6.0..."
mkdir -p "$(dirname "${AGY_PLUGIN_DIR}")"

if [[ -f "${SCRIPT_DIR}/plugin.json" ]]; then
  mkdir -p "${AGY_PLUGIN_DIR}"
  for item in plugin.json .claude-plugin gemini-extension.json pyproject.toml smithery.yaml glama.json mcp_config.json mcp_server.py hooks.json hooks README.md README.ar.md docs LICENSE sqo.py assets rules agents skills; do
    if [[ -e "${SCRIPT_DIR}/${item}" ]]; then
      cp -Rf "${SCRIPT_DIR}/${item}" "${AGY_PLUGIN_DIR}/"
    fi
  done
else
  if [[ -d "${AGY_PLUGIN_DIR}/.git" ]]; then
    git -C "${AGY_PLUGIN_DIR}" pull --ff-only
  else
    git clone --depth 1 "${REPO_URL}" "${AGY_PLUGIN_DIR}"
  fi
fi

echo "[OK] Installed v6.0 Autonomous Agent OS Suite at: ${AGY_PLUGIN_DIR}"
echo "     Active: 18 MCP Tools + Live Web UI (sqo serve) + 3-Stage Stateful Hooks + USD ROI Ledger!"
