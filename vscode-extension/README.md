# Smart Quota & Swarm Orchestrator — VS Code / Cursor / Antigravity Status-Bar Extension (`v7.0`)

Displays your real-time prevented token waste and `$USD` savings directly in the bottom status bar (`⚡ SQO: 1482.9K tok ($4.45)`) and registers 4 instant Command Palette actions:
- `Smart Quota: Open Live Web Command Center (sqo serve)`
- `Smart Quota: Run Full Workspace Doctor Check`
- `Smart Quota: Auto-Bootstrap Framework Shields & MCP (sqo init)`
- `Smart Quota: Check Session Context-Rot & Copy Handoff Brief`

## Local Development / Packaging `.vsix`
```bash
cd vscode-extension
npx @vscode/vsce package
code --install-extension smart-quota-orchestrator-vscode-7.0.0.vsix
```
