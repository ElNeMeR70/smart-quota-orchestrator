@echo off
title Antigravity Floating Quota HUD
cd /d "%~dp0"
start "" pythonw sidecars\quota_hud\desktop_widget.py
exit
