from pathlib import Path

from helix.core.installer.models import Client
from helix.core.installer.targets import TOML_MCP_FORMAT, McpConfigTarget, SnippetTarget
from helix.core.settings import Settings


def codex() -> Client:
    home = Settings.HOME_DIRECTORY
    return Client(
        key="codex",
        name="Codex CLI",
        snippet=SnippetTarget(
            global_path=home / ".codex" / "AGENTS.md",
            project_relative_path=Path("AGENTS.md"),
        ),
        extra_targets=[
            McpConfigTarget(
                global_path=home / ".codex" / "config.toml",
                project_relative_path=None,
                config_format=TOML_MCP_FORMAT,
            ),
        ],
    )
