# Git MCP Server (local)

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
