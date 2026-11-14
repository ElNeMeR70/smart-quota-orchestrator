<#
.SYNOPSIS
  One-click installer for Smart Quota & Swarm Orchestrator v4.0 Autonomous Agent OS Suite.
#>
$ErrorActionPreference = "Stop"

$RepoUrl = "https://github.com/ElNeMeR70/smart-quota-orchestrator.git"
$AgyPluginDir = Join-Path $HOME ".gemini\config\plugins\smart-quota-orchestrator"

Write-Host "==> Installing Smart Quota & Swarm Orchestrator v4.0 into Google Antigravity..." -ForegroundColor Cyan

$ParentDir = Split-Path -Parent $AgyPluginDir
if (-not (Test-Path $ParentDir)) {
    New-Item -ItemType Directory -Force -Path $ParentDir | Out-Null
}

$PluginItems = @(
    "plugin.json",
    ".claude-plugin",
    "gemini-extension.json",
    "pyproject.toml",
    "mcp_config.json",
    "mcp_server.py",
    "hooks.json",
    "hooks",
    "README.md",
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

Write-Host "[OK] Installed v4.0 Autonomous Agent OS Suite at: $AgyPluginDir" -ForegroundColor Green
Write-Host "     Active: 14 MCP Tools + 3-Stage Stateful Hooks + Incremental Code Graph + 6 Skills + 3 Subagents!" -ForegroundColor Yellow
