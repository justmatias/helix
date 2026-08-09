from pathlib import Path

from helix.core.installer.models import Client
from helix.core.installer.targets import (
    OPENCODE_MCP_FORMAT,
    McpConfigTarget,
    SnippetTarget,
)
from helix.core.settings import Settings


def opencode() -> Client:
    home = Settings.HOME_DIRECTORY
    return Client(
        key="opencode",
        name="Opencode",
        snippet=SnippetTarget(
            global_path=home / ".config" / "opencode" / "AGENTS.md",
            project_relative_path=Path("AGENTS.md"),
        ),
        extra_targets=[
            McpConfigTarget(
                global_path=home / ".config" / "opencode" / "opencode.json",
                project_relative_path=Path("opencode.json"),
                config_format=OPENCODE_MCP_FORMAT,
            ),
        ],
    )
