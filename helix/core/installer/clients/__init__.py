"""Each supported client's config paths live in their own module.

Client-specific installation *behavior* (which config files get an MCP entry
or a hook) is expressed through the ``InstallTarget``s each module puts in
``extra_targets``, not through per-client functions — every target's own
``install``/``uninstall`` already no-ops when the client has no path for it,
so there is nothing left to branch on per client.
"""

from helix.core.installer.models import Client

from .claude import claude
from .codex import codex
from .cursor import cursor
from .opencode import opencode


def all_clients() -> list[Client]:
    return [claude(), cursor(), codex(), opencode()]


__all__ = ["all_clients", "claude", "codex", "cursor", "opencode"]
