# pylint: disable=duplicate-code
from .conventions import Brain, Convention
from .installer import (
    BLOCK_PATTERN,
    END_MARKER,
    SNIPPET,
    START_MARKER,
    Client,
    Scope,
    SnippetBlock,
    clients,
    detect_installed_clients,
    detect_snippet_blocks,
    install,
    uninstall,
)
from .settings import Settings

__all__ = [
    "BLOCK_PATTERN",
    "END_MARKER",
    "SNIPPET",
    "START_MARKER",
    "Brain",
    "Client",
    "Convention",
    "Scope",
    "Settings",
    "SnippetBlock",
    "clients",
    "detect_installed_clients",
    "detect_snippet_blocks",
    "install",
    "uninstall",
]
