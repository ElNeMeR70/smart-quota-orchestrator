<#
.SYNOPSIS
  One-click installer for Smart Quota & Swarm Orchestrator v5.0 Autonomous Agent OS Suite.
#>
$ErrorActionPreference = "Stop"

$RepoUrl = "https://github.com/ElNeMeR70/smart-quota-orchestrator.git"
$AgyPluginDir = Join-Path $HOME ".gemini\config\plugins\smart-quota-orchestrator"

Write-Host "==> Installing Smart Quota & Swarm Orchestrator v6.0 into Google Antigravity..." -ForegroundColor Cyan

$ParentDir = Split-Path -Parent $AgyPluginDir
if (-not (Test-Path $ParentDir)) {
    New-Item -ItemType Directory -Force -Path $ParentDir | Out-Null
}

$PluginItems = @(
    "plugin.json",
    ".claude-plugin",
    "gemini-extension.json",
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

if (Test-Path (Join-Path $PSScriptRoot "plugin.json")) {
    New-Item -ItemType Directory -Force -Path $AgyPluginDir | Out-Null
    foreach ($item in $PluginItems) {
        $src = Join-Path $PSScriptRoot $item
        if (Test-Path $src) {
            Copy-Item -Path $src -Destination $AgyPluginDir -Recurse -Force
        }
    }
} else {
    if (Test-Path $AgyPluginDir) {
        git -C $AgyPluginDir pull --ff-only
    } else {
        git clone --depth 1 $RepoUrl $AgyPluginDir
    }
}

Write-Host "[OK] Installed v6.0 Autonomous Agent OS Suite at: $AgyPluginDir" -ForegroundColor Green
Write-Host "     Active: 18 MCP Tools + Live Web UI (`sqo serve`) + 3-Stage Hooks + `$USD ROI Ledger!" -ForegroundColor Yellow
