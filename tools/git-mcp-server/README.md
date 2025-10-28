# git-mcp-server

A minimal Model Context Protocol (MCP) server that exposes useful Git operations for the current workspace via stdio.

## Prerequisites

- Node.js 18+ and npm available on your PATH
- This folder is inside a Git repository (the server will error if not)

## Install

From the repo root:

```bash
# Install dependencies for the MCP server
(cd tools/git-mcp-server && npm install)
```

## Run (manual)

```bash
# From the repo root
node tools/git-mcp-server/src/index.js
```

The server prints a message to stderr indicating it is running. It is intended to be used by an MCP-compatible client over stdio.

## VS Code + GitHub Copilot Chat integration

This repo includes `.vscode/settings.json` to register this server with Copilot Chat:

- Enables MCP integration
- Registers the `git` server using Node and stdio transport

If Node isn’t available in your environment, install it or use a shell with Node in PATH. Then reload VS Code.

## Available tools

- `git_status` — short repo status (branch, ahead/behind, staged/unstaged, untracked)
- `git_log` — recent commits (arg: `max`, default 10)
- `git_diff` — diff (args: `range` like `HEAD~1..HEAD`, and/or `path`)
- `git_commit` — commit staged changes with message (args: `message`, `all`)
- `git_push` — push current branch (args: `remote`, `branch`)

## Troubleshooting

- “node: command not found”: install Node.js 18+ and ensure `node` is on PATH.
- “Current directory is not a Git repository”: open this folder as a Git repo (e.g., initialize with `git init` or open a cloned repo).
- Copilot Chat doesn’t list tools: ensure you reloaded VS Code after installing Node, and check `.vscode/settings.json` MCP configuration.# Git MCP Server (local)

Minimal Model Context Protocol (MCP) server exposing Git operations for this workspace.

## Tools exposed
- git_status: short repo status
- git_log: recent commits (configurable `max`)
- git_diff: working tree or commit range diff (`range`, `path`)
- git_commit: commit changes with `message` (optionally `all: true` to add .)
- git_push: push current branch (or specify `remote`, `branch`)

## Run

Install dependencies and start the server (Node 18+ recommended):

```bash
cd tools/git-mcp-server
npm install
npm start
```

This server runs over stdio and is meant to be launched by an MCP-compatible client.

## VS Code task (one-click)

You can start it from VS Code via Run Task:

1. Open the Command Palette → "Run Task"
2. Choose "Start Git MCP server" (runs in the background)

Optional: "Start Git MCP server (dev)" uses source maps.

To stop: use the "Terminate Task" action in the Task runner UI (trash can icon), or close the terminal.

### Connect from clients

- Claude Desktop / MCP-compatible tools: configure a "stdio" server pointing to `node ./src/index.js` in this folder.
- AI Toolkit (VS Code) / other MCP clients: use their MCP server configuration UI to add this server.

## Notes

- The server operates in the current working directory. Launch it from the repository root (or configure the client to set `cwd` to your repo).
- Requires an existing Git repository and network access for `git push`.
