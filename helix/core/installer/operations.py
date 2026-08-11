from pathlib import Path

from .clients import all_clients
from .hooks import HOOK_COMMAND
from .models import Client, McpConfigFormat, Scope, SnippetBlock
from .snippet import BLOCK_PATTERN, END_MARKER, SNIPPET, START_MARKER


def detect_installed_clients() -> list[Client]:
    return [client for client in all_clients() if client.installation_directory.exists()]


def _contains(path: Path | None, needle: str) -> bool:
    return path is not None and path.exists() and needle in path.read_text()


def detect_snippet_blocks(project_root: Path) -> list[SnippetBlock]:
    """Find every client+scope with a Helix snippet, MCP entry, or hook.

    A block is reported even if only the MCP config or hook survives (e.g. the
    CLAUDE.md snippet was deleted by hand) — ``uninstall``/``uninstall_mcp_config``/
    ``uninstall_hook`` are all keyed by client+scope, not by this block's path,
    so nothing is left orphaned.
    """
    blocks: list[SnippetBlock] = []
    for client in all_clients():
        for scope in Scope:
            snippet_path = client.path_for(scope, project_root)
            mcp_needle = (
                "[mcp_servers.helix]" if client.mcp_format == McpConfigFormat.TOML else '"helix"'
            )
            has_snippet = _contains(snippet_path, START_MARKER)
            has_mcp = _contains(client.mcp_path_for(scope, project_root), mcp_needle)
            has_hook = _contains(client.hook_path_for(scope, project_root), HOOK_COMMAND)
            if not (has_snippet or has_mcp or has_hook):
                continue

            display_path: Path | None = snippet_path
            if not has_snippet:
                display_path = (
                    client.mcp_path_for(scope, project_root)
                    if has_mcp
                    else client.hook_path_for(scope, project_root)
                )
            assert display_path is not None

            blocks.append(SnippetBlock(client=client, scope=scope, path=display_path))
    return blocks


def _insert_snippet_block(existing: str, block: str) -> str:
    """Return ``existing`` with the Helix snippet block inserted or refreshed.

    If a snippet block is already present, it is replaced in place
    so reinstalling updates the snippet rather than duplicating it.

    If there is other content but no existing block, the
    block is appended after a blank-line separator.

    Otherwise the block becomes the entire content.
    """
    if BLOCK_PATTERN.search(existing):
        return BLOCK_PATTERN.sub(block.rstrip("\n"), existing)
    if existing.strip():
        return existing.rstrip("\n") + "\n\n" + block
    return block


def install(client: Client, scope: Scope, project_root: Path) -> Path:
    """Write (or refresh) the Helix snippet block in the client's config file.

    Creates the file and parent directories if needed, and returns the path
    that was written.
    """
    path = client.path_for(scope, project_root)
    path.parent.mkdir(parents=True, exist_ok=True)

    existing = path.read_text() if path.exists() else (client.preamble or "")
    block = f"{START_MARKER}\n{SNIPPET}{END_MARKER}\n"
    new_text = _insert_snippet_block(existing, block)
    path.write_text(new_text)

    return path


def uninstall(client: Client, scope: Scope, project_root: Path) -> bool:
    """Remove the Helix snippet block from the client's config file.

    Deletes the file if nothing else remains. Returns ``True`` if a block was
    removed, or ``False`` if the file or block was not present.
    """
    path = client.path_for(scope, project_root)
    if not path.exists():
        return False

    text = path.read_text()
    if START_MARKER not in text:
        return False

    remaining = BLOCK_PATTERN.sub("", text).strip("\n")
    if not remaining:
        path.unlink()
        return True

    path.write_text(remaining + "\n")
    return True
