from pathlib import Path

from helix.core.installer.models import Client
from helix.core.installer.targets import JSON_MCP_FORMAT, McpConfigTarget, SnippetTarget
from helix.core.settings import Settings


def cursor() -> Client:
    home = Settings.HOME_DIRECTORY
    return Client(
        key="cursor",
        name="Cursor",
        snippet=SnippetTarget(
            global_path=home / ".cursor" / "rules" / "helix.mdc",
            project_relative_path=Path(".cursor") / "rules" / "helix.mdc",
            preamble="---\nalwaysApply: true\n---",
        ),
        detect_path=home / ".cursor",
        extra_targets=[
            McpConfigTarget(
                global_path=home / ".cursor" / "mcp.json",
                project_relative_path=Path(".cursor") / "mcp.json",
                config_format=JSON_MCP_FORMAT,
            ),
        ],
    )
