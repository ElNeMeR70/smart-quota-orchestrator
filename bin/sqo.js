#!/usr/bin/env node
/**
 * Universal Zero-Dependency Node/NPX Launcher (`npx smart-quota-orchestrator`)
 * Auto-locates Python 3 across Windows, macOS, and Linux and bridges stdio cleanly
 * for both MCP Server mode (`npx -y smart-quota-orchestrator mcp`) and all 33 CLI tools!
 */
const { spawn, spawnSync } = require("child_process");
const path = require("path");

const rootDir = path.resolve(__dirname, "..");
const userArgs = process.argv.slice(2);

function detectPython() {
  const candidates = process.platform === "win32"
    ? [["python", []], ["py", ["-3"]], ["python3", []]]
    : [["python3", []], ["python", []]];

  for (const [cmd, prefix] of candidates) {
    const check = spawnSync(cmd, [...prefix, "-c", "import sys; assert sys.version_info >= (3, 8)"], { stdio: "ignore" });
    if (check.status === 0) {
      return { cmd, prefix };
    }
  }
  console.error("[Smart Quota OS] Error: Python 3.8+ is required on PATH to run sqo-engine.");
  process.exit(1);
}

const py = detectPython();
const isMcp = userArgs[0] === "mcp" || userArgs[0] === "--mcp";
const targetScript = path.join(rootDir, isMcp ? "mcp_server.py" : "sqo.py");
const scriptArgs = isMcp ? [] : userArgs;

const child = spawn(py.cmd, [...py.prefix, targetScript, ...scriptArgs], {
  stdio: "inherit",
  env: { ...process.env, PYTHONIOENCODING: "utf-8" },
});

child.on("exit", (code) => process.exit(code ?? 0));
