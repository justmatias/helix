import json
import re
import shutil
import subprocess
from pathlib import Path
from typing import NamedTuple

from .json_config import read_json
from .models import Client, McpConfigFormat, Scope


class JsonMcpShape(NamedTuple):
    """Where and how a JSON-family format nests the "helix" server entry."""

    key: str
    entry: dict


# JSON-family formats (JSON, OPENCODE) both merge a "helix" entry into a
# top-level object; they differ only in that object's key and entry shape.
JSON_SHAPE_BY_FORMAT: dict[McpConfigFormat, JsonMcpShape] = {
    McpConfigFormat.JSON: JsonMcpShape(
        "mcpServers", {"command": "helix", "args": ["serve"]}
    ),
    McpConfigFormat.OPENCODE: JsonMcpShape(
        "mcp", {"type": "local", "command": ["helix", "serve"], "enabled": True}
    ),
}

# Codex has no comment-block convention of its own, so Helix wraps its TOML
# table in markers (like snippet.py does for markdown) rather than matching
# the table's exact text. That way a hand-added `env = ...` line inside the
# block doesn't defeat uninstall — the whole marked span comes out together.
TOML_START = "# helix-mcp:start"
TOML_END = "# helix-mcp:end"
TOML_HEADER = "[mcp_servers.helix]"
TOML_INNER = f'{TOML_HEADER}\ncommand = "helix"\nargs = ["serve"]\n'
TOML_BLOCK = f"{TOML_START}\n{TOML_INNER}{TOML_END}\n"
TOML_BLOCK_PATTERN = re.compile(
    re.escape(TOML_START) + r".*?" + re.escape(TOML_END), re.DOTALL
)

# Claude Code's global MCP scope lives in ~/.claude.json, which also holds
# live session state for a running client. Prefer the CLI's own migration
# logic over rewriting that file directly, when it's available.
CLAUDE_ADD_USER_SCOPE = [
    "claude", "mcp", "add", "-s", "user", "helix", "--", "helix", "serve",
]  # fmt: skip
CLAUDE_REMOVE_USER_SCOPE = ["claude", "mcp", "remove", "-s", "user", "helix"]


def _uses_claude_user_scope(client: Client, scope: Scope) -> bool:
    return (
        client.key == "claude"
        and scope == Scope.GLOBAL
        and shutil.which("claude") is not None
    )


def _merge_json_entry(existing: str, path: Path, fmt: McpConfigFormat) -> str:
    shape = JSON_SHAPE_BY_FORMAT[fmt]
    data = read_json(path, existing)
    data.setdefault(shape.key, {})["helix"] = shape.entry
    return json.dumps(data, indent=2) + "\n"


def _merge_toml_block(existing: str) -> str:
    if TOML_BLOCK_PATTERN.search(existing):
        return TOML_BLOCK_PATTERN.sub(TOML_BLOCK.rstrip("\n"), existing)
    if TOML_HEADER in existing:
        return existing
    if existing.strip():
        return existing.rstrip("\n") + "\n\n" + TOML_BLOCK
    return TOML_BLOCK


def _merge(existing: str, fmt: McpConfigFormat, path: Path) -> str:
    if fmt in JSON_SHAPE_BY_FORMAT:
        return _merge_json_entry(existing, path, fmt)
    return _merge_toml_block(existing)


def _remove_json_entry(existing: str, path: Path, fmt: McpConfigFormat) -> str | None:
    if not existing.strip():
        return None
    key = JSON_SHAPE_BY_FORMAT[fmt].key
    data = read_json(path, existing)
    servers = data.get(key, {})
    if "helix" not in servers:
        return None
    del servers["helix"]
    if not servers:
        del data[key]
    return json.dumps(data, indent=2) + "\n" if data else ""


def _remove_toml_block(existing: str) -> str | None:
    if TOML_BLOCK_PATTERN.search(existing):
        remaining = TOML_BLOCK_PATTERN.sub("", existing).strip("\n")
        return remaining + "\n" if remaining else ""

    # Legacy (pre-marker) installs wrote the bare table with no wrapper.
    if TOML_INNER not in existing + "\n":
        return None
    remaining = (existing + "\n").replace(TOML_INNER, "").strip("\n")
    return remaining + "\n" if remaining else ""


def _remove(existing: str, fmt: McpConfigFormat, path: Path) -> str | None:
    if fmt in JSON_SHAPE_BY_FORMAT:
        return _remove_json_entry(existing, path, fmt)
    return _remove_toml_block(existing)


def install_mcp_config(client: Client, scope: Scope, project_root: Path) -> Path | None:
    """Write (or refresh) the Helix MCP server entry in the client's MCP config file.

    Returns the path written, or ``None`` if this client has no MCP config for
    the requested scope. Raises ``InvalidConfigError`` if the existing file
    can't be parsed.
    """
    path = client.mcp_path_for(scope, project_root)
    if not path:
        return None

    if _uses_claude_user_scope(client, scope):
        subprocess.run(CLAUDE_ADD_USER_SCOPE, check=False, capture_output=True)
        return path

    path.parent.mkdir(parents=True, exist_ok=True)
    existing = path.read_text() if path.exists() else ""
    path.write_text(_merge(existing, client.mcp_format, path))
    return path


def uninstall_mcp_config(client: Client, scope: Scope, project_root: Path) -> bool:
    """Remove the Helix MCP server entry from the client's MCP config file.

    Deletes the file if nothing else remains. Returns ``True`` if the entry was
    removed, or ``False`` if the file or entry was not present. Raises
    ``InvalidConfigError`` if the existing file can't be parsed.
    """
    path = client.mcp_path_for(scope, project_root)
    if path is None:
        return False

    if _uses_claude_user_scope(client, scope):
        completed = subprocess.run(
            CLAUDE_REMOVE_USER_SCOPE, check=False, capture_output=True
        )
        return completed.returncode == 0

    if not path.exists():
        return False

    result = _remove(path.read_text(), client.mcp_format, path)
    if result is None:
        return False

    if result:
        path.write_text(result)
    else:
        path.unlink()
    return True
