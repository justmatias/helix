"""Each supported client's config paths live in their own module.

Client-specific installation *behavior* (which config files get an MCP entry
or a hook) is expressed through the ``Client`` fields each module sets, not
through per-client functions — ``operations.install``, ``hooks.install_hook``,
and ``mcp_config.install_mcp_config`` already no-op for clients that don't
set the relevant path, so there is nothing left to branch on per client.
"""

from ..models import Client
from .claude import claude
from .codex import codex
from .cursor import cursor
from .opencode import opencode


def all_clients() -> list[Client]:
    return [claude(), cursor(), codex(), opencode()]


__all__ = ["all_clients", "claude", "codex", "cursor", "opencode"]
