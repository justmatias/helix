from pathlib import Path

from helix.core.installer.models import Client
from helix.core.installer.scope import Scope
from helix.core.installer.targets import (
    CLAUDE_ADD_USER_SCOPE,
    CLAUDE_REMOVE_USER_SCOPE,
    JSON_MCP_FORMAT,
    HookTarget,
    McpConfigTarget,
    SnippetTarget,
    SubprocessInstallTarget,
)
from helix.core.settings import Settings


def claude() -> Client:
    home = Settings.HOME_DIRECTORY
    return Client(
        key="claude",
        name="Claude Code",
        snippet=SnippetTarget(
            global_path=home / ".claude" / "CLAUDE.md",
            project_relative_path=Path("CLAUDE.md"),
        ),
        extra_targets=[
            SubprocessInstallTarget(
                fallback=McpConfigTarget(
                    global_path=home / ".claude.json",
                    project_relative_path=Path(".mcp.json"),
                    config_format=JSON_MCP_FORMAT,
                ),
                subprocess_scope=Scope.GLOBAL,
                add_command=CLAUDE_ADD_USER_SCOPE,
                remove_command=CLAUDE_REMOVE_USER_SCOPE,
            ),
            HookTarget(
                global_path=home / ".claude" / "settings.json",
                project_relative_path=Path(".claude") / "settings.json",
            ),
        ],
    )
