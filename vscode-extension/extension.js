const vscode = require("vscode");
const { execFile } = require("child_process");
const path = require("path");
const os = require("os");
const fs = require("fs");

function resolveSqoPy() {
  const candidates = [
    path.join(os.homedir(), ".gemini", "config", "plugins", "smart-quota-orchestrator", "sqo.py"),
    path.resolve(__dirname, "..", "sqo.py"),
  ];
  return candidates.find((p) => fs.existsSync(p)) || candidates[1];
}

function getWorkspaceRoot() {
  const folders = vscode.workspace.workspaceFolders;
  return folders && folders.length > 0 ? folders[0].uri.fsPath : os.homedir();
}

function activate(context) {
  const statusBar = vscode.window.createStatusBarItem(vscode.StatusBarAlignment.Right, 100);
  statusBar.command = "sqo.openLiveCenter";
  statusBar.text = "$(zap) SQO: Ready";
  statusBar.tooltip = "Smart Quota & Swarm Orchestrator v7.0 — Click to open Live Command Center";
  statusBar.show();
  context.subscriptions.push(statusBar);

  function refreshRoiBadge() {
    const sqoPy = resolveSqoPy();
    if (!fs.existsSync(sqoPy)) return;
    execFile("python", [sqoPy, "roi", "--format", "json"], { timeout: 4000 }, (err, stdout) => {
      if (err || !stdout) return;
      try {
        const d = JSON.parse(stdout);
        const tokK = (d.total_tokens_saved / 1000).toFixed(1);
        const usd = d.usd_equivalents.balanced_sonnet_carbon.saved_usd.toFixed(2);
        statusBar.text = `$(shield) SQO: ${tokK}K tok ($${usd})`;
      } catch (_) {}
    });
  }

  refreshRoiBadge();
  const timer = setInterval(refreshRoiBadge, 15000);
  context.subscriptions.push({ dispose: () => clearInterval(timer) });

  context.subscriptions.push(
    vscode.commands.registerCommand("sqo.openLiveCenter", () => {
      const term = vscode.window.createTerminal("Smart Quota Live Center");
      term.show();
      term.sendText(`python "${resolveSqoPy()}" serve --workspace "${getWorkspaceRoot()}" --open`);
    }),
    vscode.commands.registerCommand("sqo.runDoctor", () => {
      const term = vscode.window.createTerminal("Smart Quota Doctor");
      term.show();
      term.sendText(`python "${resolveSqoPy()}" doctor --workspace "${getWorkspaceRoot()}"`);
    }),
    vscode.commands.registerCommand("sqo.initWorkspace", () => {
      const term = vscode.window.createTerminal("Smart Quota Init");
      term.show();
      term.sendText(`python "${resolveSqoPy()}" init --workspace "${getWorkspaceRoot()}"`);
    }),
    vscode.commands.registerCommand("sqo.checkContextRot", () => {
      const term = vscode.window.createTerminal("Smart Quota Context Health");
      term.show();
      term.sendText(`python "${resolveSqoPy()}" context-health --workspace "${getWorkspaceRoot()}"`);
    })
  );
}

function deactivate() {}
module.exports = { activate, deactivate };
