import json
import sys
import urllib.request
from pathlib import Path

BASE_URL = "http://127.0.0.1:8088/mcp"
AUTH_TOKEN = json.loads((Path(__file__).resolve().parents[1] / ".mcp.json").read_text(encoding="utf-8"))["mcpServers"]["VibeUE"]["headers"]["Authorization"]
PROTOCOL_VERSION = "2025-11-25"


def post(payload, session_id=None):
    body = json.dumps(payload).encode("utf-8")
    headers = {
        "Authorization": AUTH_TOKEN,
        "Content-Type": "application/json",
        "Accept": "application/json",
        "MCP-Protocol-Version": PROTOCOL_VERSION,
    }
    if session_id:
        headers["Mcp-Session-Id"] = session_id
    req = urllib.request.Request(BASE_URL, data=body, headers=headers, method="POST")
    with urllib.request.urlopen(req, timeout=60) as resp:
        text = resp.read().decode("utf-8")
        session = resp.headers.get("mcp-session-id")
    if not text.strip():
        return session, None
    return session, json.loads(text)


def main():
    if len(sys.argv) < 3:
        print("Usage: vibeue_call.py <tool_name> <json_args|@file|- >", file=sys.stderr)
        sys.exit(2)

    tool_name = sys.argv[1]
    raw_args = sys.argv[2]
    if raw_args == "-":
        raw_args = sys.stdin.read()
    elif raw_args.startswith("@"):
        with open(raw_args[1:], "r", encoding="utf-8") as fh:
            raw_args = fh.read()
    tool_args = json.loads(raw_args)

    session_id, _ = post(
        {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "initialize",
            "params": {
                "protocolVersion": PROTOCOL_VERSION,
                "capabilities": {},
                "clientInfo": {"name": "codex-local-client", "version": "1.0"},
            },
        }
    )
    post(
        {"jsonrpc": "2.0", "method": "notifications/initialized", "params": {}},
        session_id=session_id,
    )
    _, result = post(
        {
            "jsonrpc": "2.0",
            "id": 2,
            "method": "tools/call",
            "params": {"name": tool_name, "arguments": tool_args},
        },
        session_id=session_id,
    )
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
