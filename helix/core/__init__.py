# pylint: disable=duplicate-code
from .conventions import Brain, Convention
from .installer import (
    BLOCK_PATTERN,
    END_MARKER,
    HOOK_COMMAND,
    HOOK_EVENT,
    SNIPPET,
    START_MARKER,
    Client,
    InstallTarget,
    InvalidConfigError,
    Scope,
    SnippetBlock,
    clients,
    detect_installed_clients,
    detect_snippet_blocks,
)
from .settings import Settings

__all__ = [
    "BLOCK_PATTERN",
    "END_MARKER",
    "HOOK_COMMAND",
    "HOOK_EVENT",
    "SNIPPET",
    "START_MARKER",
    "Brain",
    "Client",
    "Convention",
    "InstallTarget",
    "InvalidConfigError",
    "Scope",
    "Settings",
    "SnippetBlock",
    "clients",
    "detect_installed_clients",
    "detect_snippet_blocks",
]
