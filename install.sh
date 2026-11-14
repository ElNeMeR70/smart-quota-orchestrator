#!/usr/bin/env bash
set -euo pipefail

REPO_URL="https://github.com/ElNeMeR70/smart-quota-orchestrator.git"
AGY_PLUGIN_DIR="${HOME}/.gemini/config/plugins/smart-quota-orchestrator"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

echo "==> Installing Smart Quota & Swarm Orchestrator v4.0..."
mkdir -p "$(dirname "${AGY_PLUGIN_DIR}")"

if [[ -f "${SCRIPT_DIR}/plugin.json" ]]; then
  rm -rf "${AGY_PLUGIN_DIR}"
  mkdir -p "${AGY_PLUGIN_DIR}"
  for item in plugin.json .claude-plugin gemini-extension.json pyproject.toml mcp_config.json mcp_server.py hooks.json hooks README.md LICENSE sqo.py assets rules agents skills; do
    if [[ -e "${SCRIPT_DIR}/${item}" ]]; then
      cp -R "${SCRIPT_DIR}/${item}" "${AGY_PLUGIN_DIR}/"
    fi
  done
else
  if [[ -d "${AGY_PLUGIN_DIR}/.git" ]]; then
    git -C "${AGY_PLUGIN_DIR}" pull --ff-only
  else
    git clone --depth 1 "${REPO_URL}" "${AGY_PLUGIN_DIR}"
  fi
fi

echo "[OK] Installed v4.0 Autonomous Agent OS Suite at: ${AGY_PLUGIN_DIR}"
echo "     Active: 14 MCP Tools + 3-Stage Stateful Hooks + Incremental Code Graph + 6 Skills + 3 Subagents!"
