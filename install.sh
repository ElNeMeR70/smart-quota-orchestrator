#!/usr/bin/env bash
set -euo pipefail

REPO_URL="https://github.com/ElNeMeR70/smart-quota-orchestrator.git"
AGY_PLUGIN_DIR="${HOME}/.gemini/config/plugins/smart-quota-orchestrator"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

echo "==> Installing Smart Quota & Swarm Orchestrator..."
mkdir -p "$(dirname "${AGY_PLUGIN_DIR}")"

if [[ -f "${SCRIPT_DIR}/plugin.json" ]]; then
  rm -rf "${AGY_PLUGIN_DIR}"
  mkdir -p "${AGY_PLUGIN_DIR}"
  cp -R "${SCRIPT_DIR}/." "${AGY_PLUGIN_DIR}/"
  rm -rf "${AGY_PLUGIN_DIR}/.git"
else
  if [[ -d "${AGY_PLUGIN_DIR}/.git" ]]; then
    git -C "${AGY_PLUGIN_DIR}" pull --ff-only
  else
    git clone --depth 1 "${REPO_URL}" "${AGY_PLUGIN_DIR}"
  fi
fi

echo "[OK] Installed at: ${AGY_PLUGIN_DIR}"
echo "     Restart or start a new turn in Google Antigravity to activate!"
