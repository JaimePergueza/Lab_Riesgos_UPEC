import { readFile } from "node:fs/promises";
const BASE_URL = "http://127.0.0.1:8088/mcp";
const AUTH_TOKEN = JSON.parse(await readFile(new URL("../.mcp.json", import.meta.url), "utf8")).mcpServers.VibeUE.headers.Authorization;
const PROTOCOL_VERSION = "2025-11-25";

async function post(payload, sessionId = null) {
  const headers = {
    Authorization: AUTH_TOKEN,
    "Content-Type": "application/json",
    Accept: "application/json",
    "MCP-Protocol-Version": PROTOCOL_VERSION,
    Connection: "close",
  };
  if (sessionId) headers["Mcp-Session-Id"] = sessionId;

  const res = await fetch(BASE_URL, {
    method: "POST",
    headers,
    body: JSON.stringify(payload),
  });
  const text = await res.text();
  return {
    sessionId: res.headers.get("mcp-session-id"),
    json: text.trim() ? JSON.parse(text) : null,
  };
}

async function main() {
  if (process.argv.length < 4) {
    console.error("Usage: node vibeue_call.mjs <tool_name> <json_args|@file>");
    process.exit(2);
  }

  const toolName = process.argv[2];
  let rawArgs = process.argv[3];
  if (rawArgs.startsWith("@")) {
    rawArgs = await (await import("node:fs/promises")).readFile(rawArgs.slice(1), "utf8");
  }
  const toolArgs = JSON.parse(rawArgs);

  const init = await post({
    jsonrpc: "2.0",
    id: 1,
    method: "initialize",
    params: {
      protocolVersion: PROTOCOL_VERSION,
      capabilities: {},
      clientInfo: { name: "codex-local-client", version: "1.0" },
    },
  });
  const sessionId = init.sessionId;

  await post(
    { jsonrpc: "2.0", method: "notifications/initialized", params: {} },
    sessionId,
  );

  const result = await post(
    {
      jsonrpc: "2.0",
      id: 2,
      method: "tools/call",
      params: { name: toolName, arguments: toolArgs },
    },
    sessionId,
  );

  console.log(JSON.stringify(result.json, null, 2));
}

main().catch((error) => {
  console.error(error);
  process.exit(1);
});
