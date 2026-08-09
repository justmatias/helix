from pathlib import Path

from .clients import all_clients as clients
from .models import Client, Scope, SnippetBlock


def detect_installed_clients() -> list[Client]:
    return [client for client in clients() if client.installation_directory.exists()]


def detect_snippet_blocks(project_root: Path) -> list[SnippetBlock]:
    """Find every client+scope with any Helix target present.

    A block is reported even if only the MCP config or hook survives (e.g. the
    CLAUDE.md snippet was deleted by hand) — each target's own
    ``install``/``uninstall`` is keyed by client+scope, not by this block's
    path, so nothing is left orphaned.
    """
    blocks: list[SnippetBlock] = []
    for client in clients():
        for scope in Scope:
            present = [
                target for target in client.all_targets if target.exists(scope, project_root)
            ]
            if not present:
                continue

            display_path = present[0].path_for(scope, project_root)
            assert display_path is not None
            blocks.append(SnippetBlock(client=client, scope=scope, path=display_path))
    return blocks
