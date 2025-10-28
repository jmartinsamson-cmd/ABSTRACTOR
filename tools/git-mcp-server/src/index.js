// Minimal Git MCP server using @modelcontextprotocol/sdk over stdio
import { Server } from "@modelcontextprotocol/sdk/server/index.js";
import { StdioServerTransport } from "@modelcontextprotocol/sdk/server/stdio.js";
import {
  ListToolsRequestSchema,
  CallToolRequestSchema,
  ListToolsResultSchema,
  CompatibilityCallToolResultSchema,
} from "@modelcontextprotocol/sdk/types.js";
import simpleGit from "simple-git";
import { resolve } from "node:path";
import { fileURLToPath } from "node:url";
import { cwd as processCwd } from "node:process";

const CWD = processCwd();
const git = simpleGit({ baseDir: CWD });

async function ensureRepo() {
  const isRepo = await git.checkIsRepo();
  if (!isRepo) {
    throw new Error("Current directory is not a Git repository");
  }
}

const server = new Server(
  {
    name: "git-mcp-server",
    version: "0.1.0",
  },
  {
    capabilities: {
      tools: {}
    }
  }
);

// Tools registry
const tools = {
  git_status: {
    description:
      "Get short git status (branch, ahead/behind, staged/unstaged, untracked)",
    inputSchema: { type: "object", properties: {} },
    handler: async () => {
      await ensureRepo();
      const status = await git.status();
      return { content: [{ type: "text", text: JSON.stringify(status, null, 2) }] };
    },
  },
  git_log: {
    description: "List recent commits",
    inputSchema: {
      type: "object",
      properties: { max: { type: "number", default: 10 } },
    },
    handler: async ({ max = 10 } = {}) => {
      await ensureRepo();
      const log = await git.log({ maxCount: max });
      return { content: [{ type: "text", text: JSON.stringify(log.all, null, 2) }] };
    },
  },
  git_diff: {
    description:
      "Show diff. If no args, shows working tree diff. Optionally provide a path or a commit range (e.g., 'HEAD~1..HEAD').",
    inputSchema: {
      type: "object",
      properties: {
        range: { type: "string", description: "Commit range, e.g., HEAD~1..HEAD" },
        path: { type: "string", description: "Optional pathspec to limit diff" },
      },
    },
    handler: async ({ range, path } = {}) => {
      await ensureRepo();
      let args = ["diff"];
      if (range) args.push(range);
      if (path) args.push("--", path);
      const result = await git.raw(args);
      return { content: [{ type: "text", text: result || "(no diff)" }] };
    },
  },
  git_commit: {
    description:
      "Commit staged changes with a message. Optionally add all changes before committing.",
    inputSchema: {
      type: "object",
      required: ["message"],
      properties: {
        message: { type: "string" },
        all: { type: "boolean", default: false },
      },
    },
    handler: async ({ message, all = false }) => {
      await ensureRepo();
      if (all) await git.add(["."]);
      const res = await git.commit(message);
      return { content: [{ type: "text", text: JSON.stringify(res, null, 2) }] };
    },
  },
  git_push: {
    description:
      "Push the current branch to origin (or specified remote/branch)",
    inputSchema: {
      type: "object",
      properties: {
        remote: { type: "string", default: "origin" },
        branch: { type: "string" },
      },
    },
    handler: async ({ remote = "origin", branch } = {}) => {
      await ensureRepo();
      let current = branch;
      if (!current) {
        const status = await git.status();
        current = status.current;
      }
      const res = await git.push(remote, current);
      return { content: [{ type: "text", text: JSON.stringify(res, null, 2) }] };
    },
  },
};

// Register MCP tool handlers
server.setRequestHandler(ListToolsRequestSchema, async () => {
  const toolList = Object.entries(tools).map(([name, t]) => ({
    name,
    description: t.description,
    inputSchema: t.inputSchema,
  }));
  return { tools: toolList };
});

server.setRequestHandler(CallToolRequestSchema, async (req) => {
  const { name, arguments: args } = req.params ?? {};
  const tool = tools[name];
  if (!tool) {
    return { content: [{ type: "text", text: `Unknown tool: ${name}` }], isError: true };
  }
  try {
    const result = await tool.handler(args ?? {});
    return result;
  } catch (e) {
    return { content: [{ type: "text", text: String(e?.message || e) }], isError: true };
  }
});

// Start stdio transport
const transport = new StdioServerTransport();
await server.connect(transport);
console.error("git-mcp-server is running on stdio. Launch it via an MCP-compatible client.");
