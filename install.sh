#!/usr/bin/env bash
set -euo pipefail

REPO_URL="https://github.com/ElNeMeR70/smart-quota-orchestrator.git"
AGY_PLUGIN_DIR="${HOME}/.gemini/config/plugins/smart-quota-orchestrator"
SCRIPT_DIR=""
if [[ -n "${BASH_SOURCE[0]:-}" && -f "${BASH_SOURCE[0]}" ]]; then
  SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
fi

echo "==> Installing Smart Quota & Swarm Orchestrator v9.0 Omniscient..."
mkdir -p "$(dirname "${AGY_PLUGIN_DIR}")"

if [[ -n "${SCRIPT_DIR}" && -f "${SCRIPT_DIR}/plugin.json" ]]; then
  mkdir -p "${AGY_PLUGIN_DIR}"
  for item in plugin.json .claude-plugin gemini-extension.json package.json bin vscode-extension pyproject.toml smithery.yaml glama.json mcp_config.json mcp_server.py hooks.json hooks README.md README.ar.md docs LICENSE sqo.py assets rules agents skills; do
    if [[ -e "${SCRIPT_DIR}/${item}" ]]; then
      cp -Rf "${SCRIPT_DIR}/${item}" "${AGY_PLUGIN_DIR}/"
    fi
  done
else
  if [[ -d "${AGY_PLUGIN_DIR}/.git" ]]; then
    git -C "${AGY_PLUGIN_DIR}" pull --ff-only
  elif [[ -d "${AGY_PLUGIN_DIR}" ]]; then
    TMP_CLONE="$(mktemp -d)"
    git clone --depth 1 "${REPO_URL}" "${TMP_CLONE}"
    cp -Rf "${TMP_CLONE}/." "${AGY_PLUGIN_DIR}/"
    rm -rf "${TMP_CLONE}"
  else
    git clone --depth 1 "${REPO_URL}" "${AGY_PLUGIN_DIR}"
  fi
fi

echo "[OK] Installed v9.0 Omniscient Suite at: ${AGY_PLUGIN_DIR}"
echo "     Active: 31 MCP Tools + 45 CLI Commands + Anti-Hallucination + i18n Matrix + Memo Cache + Hive-Mind!"
echo "     Live Platform & Playground: https://sqo.elnemer-ai.com"
