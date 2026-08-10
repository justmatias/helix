from pathlib import Path

from helix.core.installer.models import Client, McpConfigFormat
from helix.core.settings import Settings


def codex() -> Client:
    home = Settings.HOME_DIRECTORY
    return Client(
        key="codex",
        name="Codex CLI",
        global_path=home / ".codex" / "AGENTS.md",
        project_relative_path=Path("AGENTS.md"),
        mcp_global_path=home / ".codex" / "config.toml",
        mcp_format=McpConfigFormat.TOML,
    )
