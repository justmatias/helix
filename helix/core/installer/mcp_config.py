import json
from pathlib import Path

from .models import Client, McpConfigFormat, Scope

HELIX_ENTRY = {"command": "helix", "args": ["serve"]}
TOML_HEADER = "[mcp_servers.helix]"
TOML_BLOCK = '[mcp_servers.helix]\ncommand = "helix"\nargs = ["serve"]\n'


def _merge(existing: str, fmt: McpConfigFormat) -> str:
    if fmt == McpConfigFormat.JSON:
        data: dict = json.loads(existing) if existing.strip() else {}
        data.setdefault("mcpServers", {})["helix"] = HELIX_ENTRY
        return json.dumps(data, indent=2) + "\n"

    if TOML_HEADER in existing:
        return existing
    if existing.strip():
        return existing.rstrip("\n") + "\n\n" + TOML_BLOCK
    return TOML_BLOCK


def _remove(existing: str, fmt: McpConfigFormat) -> str | None:
    if fmt == McpConfigFormat.JSON:
        if not existing.strip():
            return None
        data: dict = json.loads(existing)
        servers = data.get("mcpServers", {})
        if "helix" not in servers:
            return None
        del servers["helix"]
        if not servers:
            del data["mcpServers"]
        return json.dumps(data, indent=2) + "\n" if data else ""

    if TOML_BLOCK not in existing + "\n":
        return None
    remaining = (existing + "\n").replace(TOML_BLOCK, "").strip("\n")
    return remaining + "\n" if remaining else ""


def install_mcp_config(client: Client, scope: Scope, project_root: Path) -> Path | None:
    """Write (or refresh) the Helix MCP server entry in the client's MCP config file.

    Returns the path written, or ``None`` if this client has no MCP config for
    the requested scope.
    """
    path = client.mcp_path_for(scope, project_root)
    if not path:
        return None

    path.parent.mkdir(parents=True, exist_ok=True)
    existing = path.read_text() if path.exists() else ""
    path.write_text(_merge(existing, client.mcp_format))
    return path


def uninstall_mcp_config(client: Client, scope: Scope, project_root: Path) -> bool:
    """Remove the Helix MCP server entry from the client's MCP config file.

    Deletes the file if nothing else remains. Returns ``True`` if the entry was
    removed, or ``False`` if the file or entry was not present.
    """
    path = client.mcp_path_for(scope, project_root)
    if path is None or not path.exists():
        return False

    result = _remove(path.read_text(), client.mcp_format)
    if result is None:
        return False

    if result:
        path.write_text(result)
    else:
        path.unlink()
    return True
