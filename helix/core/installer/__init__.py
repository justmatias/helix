# pylint: disable=duplicate-code  # re-export list mirrors helix.core
from helix.core.installer.models import Client, Scope, SnippetBlock
from helix.core.installer.operations import (
    clients,
    detect_installed_clients,
    detect_snippet_blocks,
    install,
    uninstall,
)
from helix.core.installer.snippet import (
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
    "SnippetBlock",
    "Scope",
    "clients",
    "detect_snippet_blocks",
    "detect_installed_clients",
    "install",
    "uninstall",
]
