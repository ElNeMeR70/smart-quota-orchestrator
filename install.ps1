<#
.SYNOPSIS
  One-click installer for Smart Quota & Swarm Orchestrator v7.0 Global Ecosystem Suite (https://sqo.elnemer-ai.com).
#>
$ErrorActionPreference = "Stop"

$RepoUrl = "https://github.com/ElNeMeR70/smart-quota-orchestrator.git"
$AgyPluginDir = Join-Path $HOME ".gemini\config\plugins\smart-quota-orchestrator"

Write-Host "==> Installing Smart Quota & Swarm Orchestrator v8.0 Singularity into Google Antigravity..." -ForegroundColor Cyan

$ParentDir = Split-Path -Parent $AgyPluginDir
if (-not (Test-Path $ParentDir)) {
    New-Item -ItemType Directory -Force -Path $ParentDir | Out-Null
}

$PluginItems = @(
    "plugin.json",
    ".claude-plugin",
    "gemini-extension.json",
    "package.json",
    "bin",
    "vscode-extension",
    "pyproject.toml",
    "smithery.yaml",
    "glama.json",
    "mcp_config.json",
    "mcp_server.py",
    "hooks.json",
    "hooks",
    "README.md",
    "README.ar.md",
    "docs",
    "LICENSE",
    "sqo.py",
    "assets",
    "rules",
    "agents",
    "skills"
)

if ($PSScriptRoot -and (Test-Path (Join-Path $PSScriptRoot "plugin.json"))) {
    New-Item -ItemType Directory -Force -Path $AgyPluginDir | Out-Null
    foreach ($item in $PluginItems) {
        $src = Join-Path $PSScriptRoot $item
        if (Test-Path $src) {
            Copy-Item -Path $src -Destination $AgyPluginDir -Recurse -Force
        }
    }
} else {
    if (Test-Path (Join-Path $AgyPluginDir ".git")) {
        git -C $AgyPluginDir pull --ff-only
    } elseif (Test-Path $AgyPluginDir) {
        $TmpClone = Join-Path ([System.IO.Path]::GetTempPath()) ("sqo_install_" + [guid]::NewGuid().ToString("N"))
        git clone --depth 1 $RepoUrl $TmpClone
        Copy-Item -Path (Join-Path $TmpClone "*") -Destination $AgyPluginDir -Recurse -Force
        Remove-Item -Recurse -Force $TmpClone -ErrorAction SilentlyContinue
    } else {
        git clone --depth 1 $RepoUrl $AgyPluginDir
    }
}

Write-Host "[OK] Installed v8.0 Singularity Edition at: $AgyPluginDir" -ForegroundColor Green
Write-Host "     Active: 25 MCP Tools + 39 CLI Commands + Hive-Mind + Schema Distiller + Time-Machine + `$USD ROI Ledger!" -ForegroundColor Yellow
Write-Host "     Live Playground & Docs: https://sqo.elnemer-ai.com" -ForegroundColor Cyan
