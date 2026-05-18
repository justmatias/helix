from pathlib import Path

from helix.core.settings import Settings

from .models import Client, Scope, SnippetBlock
from .snippet import BLOCK_PATTERN, END_MARKER, SNIPPET, START_MARKER


def clients() -> list[Client]:
    home = Settings.HOME_DIRECTORY
    return [
        Client(
            key="claude",
            name="Claude Code",
            global_path=home / ".claude" / "CLAUDE.md",
            project_relative_path=Path("CLAUDE.md"),
        ),
        Client(
            key="cursor",
            name="Cursor",
            global_path=home / ".cursor" / "rules" / "helix.mdc",
            project_relative_path=Path(".cursor") / "rules" / "helix.mdc",
        ),
        Client(
            key="codex",
            name="Codex CLI",
            global_path=home / ".codex" / "AGENTS.md",
            project_relative_path=Path("AGENTS.md"),
        ),
        Client(
            key="opencode",
            name="Opencode",
            global_path=home / ".config" / "opencode" / "AGENTS.md",
            project_relative_path=Path("AGENTS.md"),
        ),
    ]


def detect_installed_clients() -> list[Client]:
    return [client for client in clients() if client.global_path.parent.exists()]


def detect_snippet_blocks(project_root: Path) -> list[SnippetBlock]:
    blocks: list[SnippetBlock] = []
    for client in clients():
        for scope in Scope:
            path = client.path_for(scope, project_root)
            if not path.exists():
                continue

            if not START_MARKER in path.read_text():
                continue

            config_block = SnippetBlock(client=client, scope=scope, path=path)
            blocks.append(config_block)
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

    existing = path.read_text() if path.exists() else ""
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
