# pylint: disable=duplicate-code
from .hooks import install_hook, uninstall_hook
from .mcp_config import install_mcp_config, uninstall_mcp_config
from .models import Client, McpConfigFormat, Scope, SnippetBlock
from .operations import (
    clients,
    detect_installed_clients,
    detect_snippet_blocks,
    install,
    uninstall,
)
from .snippet import (
    BLOCK_PATTERN,
    END_MARKER,
    SNIPPET,
    START_MARKER,
)

__all__ = [
    "BLOCK_PATTERN",
    "END_MARKER",
    "SNIPPET",
    "START_MARKER",
    "Client",
    "McpConfigFormat",
    "Scope",
    "SnippetBlock",
    "clients",
    "detect_installed_clients",
    "detect_snippet_blocks",
    "install",
    "install_hook",
    "install_mcp_config",
    "uninstall",
    "uninstall_hook",
    "uninstall_mcp_config",
]
