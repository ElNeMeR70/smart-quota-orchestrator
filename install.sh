#!/usr/bin/env bash
set -euo pipefail

REPO_URL="https://github.com/ElNeMeR70/smart-quota-orchestrator.git"
AGY_PLUGIN_DIR="${HOME}/.gemini/config/plugins/smart-quota-orchestrator"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

echo "==> Installing Smart Quota & Swarm Orchestrator v2.0..."
mkdir -p "$(dirname "${AGY_PLUGIN_DIR}")"

if [[ -f "${SCRIPT_DIR}/plugin.json" ]]; then
  rm -rf "${AGY_PLUGIN_DIR}"
  mkdir -p "${AGY_PLUGIN_DIR}"
  for item in plugin.json .claude-plugin gemini-extension.json README.md LICENSE sqo.py assets rules agents skills; do
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

echo "[OK] Installed v2.0 at: ${AGY_PLUGIN_DIR}"
echo "     Restart or start a new turn in Google Antigravity to activate!"
