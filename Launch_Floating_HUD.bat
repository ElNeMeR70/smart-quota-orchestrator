@echo off
title Antigravity Floating Quota HUD
cd /d "%~dp0"

netstat -ano | findstr ":7899" >nul
if %errorlevel% neq 0 (
    start "" pythonw sidecars\quota_hud\server.py
    timeout /t 1 /nobreak >nul
)

start "" pythonw sidecars\quota_hud\desktop_widget.py
exit
