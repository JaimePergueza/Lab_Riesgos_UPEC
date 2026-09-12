import json
import sys
import urllib.error
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CFG = ROOT / ".mcp.json"

def load_auth_header():
    data = json.loads(CFG.read_text(encoding="utf-8"))
    return data["mcpServers"]["VibeUE"]["headers"]["Authorization"]

def mcp_call(method, params=None, req_id=1):
    payload = {"jsonrpc": "2.0", "id": req_id, "method": method}
    if params is not None:
        payload["params"] = params
    req = urllib.request.Request(
        "http://127.0.0.1:8088/mcp",
        data=json.dumps(payload).encode("utf-8"),
        headers={
            "Authorization": load_auth_header(),
            "Content-Type": "application/json",
        },
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=15) as resp:
        return json.loads(resp.read().decode("utf-8"))

def main():
    if not CFG.exists():
        print("FAIL: missing .mcp.json")
        return 1

    try:
        init = mcp_call(
            "initialize",
            {
                "protocolVersion": "2024-11-05",
                "capabilities": {},
                "clientInfo": {"name": "cursor-check", "version": "1.0"},
            },
            1,
        )
        print("INIT_OK")
        print(json.dumps(init, ensure_ascii=False)[:500])

        tools = mcp_call("tools/list", {}, 2)
        tool_names = [
            t.get("name", "?")
            for t in tools.get("result", {}).get("tools", [])
        ]
        print("TOOLS_OK", len(tool_names))
        print(", ".join(tool_names[:20]))

        code = """
import unreal
print("ENGINE_VERSION:", unreal.SystemLibrary.get_engine_version())
asset_registry = unreal.AssetRegistryHelpers.get_asset_registry()
filter = unreal.ARFilter(class_names=["Blueprint"], recursive_paths=True)
assets = asset_registry.get_assets(filter)
print("BLUEPRINT_COUNT:", len(assets))
for asset in sorted(assets, key=lambda a: str(a.package_name)):
    print(str(asset.package_name))
""".strip()

        result = mcp_call(
            "tools/call",
            {"name": "execute_python_code", "arguments": {"code": code}},
            3,
        )
        print("EXEC_OK")
        content = result.get("result", {}).get("content", [])
        for item in content:
            if item.get("type") == "text":
                print(item.get("text", ""))
        return 0
    except urllib.error.URLError as exc:
        print("FAIL: cannot reach VibeUE on http://127.0.0.1:8088/mcp")
        print(str(exc))
        return 2
    except Exception as exc:
        print("FAIL:", type(exc).__name__, exc)
        return 3

if __name__ == "__main__":
    sys.exit(main())
