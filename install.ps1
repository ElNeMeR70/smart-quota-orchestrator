<#
.SYNOPSIS
  One-click installer for Smart Quota & Swarm Orchestrator (Google Antigravity + Claude Code).
#>
$ErrorActionPreference = "Stop"

$RepoUrl = "https://github.com/ElNeMeR70/smart-quota-orchestrator.git"
$AgyPluginDir = Join-Path $HOME ".gemini\config\plugins\smart-quota-orchestrator"

Write-Host "==> Installing Smart Quota & Swarm Orchestrator into Google Antigravity..." -ForegroundColor Cyan

$ParentDir = Split-Path -Parent $AgyPluginDir
if (-not (Test-Path $ParentDir)) {
    New-Item -ItemType Directory -Force -Path $ParentDir | Out-Null
}

if (Test-Path (Join-Path $PSScriptRoot "plugin.json")) {
    if (Test-Path $AgyPluginDir) { Remove-Item -Recurse -Force $AgyPluginDir }
    New-Item -ItemType Directory -Force -Path $AgyPluginDir | Out-Null
    Copy-Item -Path (Join-Path $PSScriptRoot "*") -Destination $AgyPluginDir -Recurse -Force -Exclude ".git"
} else {
    if (Test-Path $AgyPluginDir) {
        git -C $AgyPluginDir pull --ff-only
    } else {
        git clone --depth 1 $RepoUrl $AgyPluginDir
    }
}

Write-Host "[OK] Installed at: $AgyPluginDir" -ForegroundColor Green
Write-Host "     Open Google Antigravity -> Customizations -> Plugins to view 'Smart Quota & Swarm Orchestrator'!" -ForegroundColor Yellow
