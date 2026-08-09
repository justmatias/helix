# pylint: disable=duplicate-code
from .clients import all_clients as clients
from .errors import InvalidConfigError
from .models import Client, SnippetBlock
from .operations import detect_installed_clients, detect_snippet_blocks
from .scope import Scope
from .targets import (
    BLOCK_PATTERN,
    END_MARKER,
    HOOK_COMMAND,
    HOOK_EVENT,
    JSON_MCP_FORMAT,
    OPENCODE_MCP_FORMAT,
    SNIPPET,
    START_MARKER,
    TOML_END,
    TOML_MCP_FORMAT,
    TOML_START,
    ConfigFormat,
    HookTarget,
    InstallTarget,
    McpConfigTarget,
    SnippetTarget,
    SubprocessInstallTarget,
    TextInstallTarget,
)

__all__ = [
    "BLOCK_PATTERN",
    "END_MARKER",
    "HOOK_COMMAND",
    "HOOK_EVENT",
    "JSON_MCP_FORMAT",
    "OPENCODE_MCP_FORMAT",
    "SNIPPET",
    "START_MARKER",
    "TOML_END",
    "TOML_MCP_FORMAT",
    "TOML_START",
    "Client",
    "ConfigFormat",
    "HookTarget",
    "InstallTarget",
    "InvalidConfigError",
    "McpConfigTarget",
    "Scope",
    "SnippetBlock",
    "SnippetTarget",
    "SubprocessInstallTarget",
    "TextInstallTarget",
    "clients",
    "detect_installed_clients",
    "detect_snippet_blocks",
]
