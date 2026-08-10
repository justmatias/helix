from pathlib import Path

from helix.core.settings import Settings

from ..models import Client


def claude() -> Client:
    home = Settings.HOME_DIRECTORY
    return Client(
        key="claude",
        name="Claude Code",
        global_path=home / ".claude" / "CLAUDE.md",
        project_relative_path=Path("CLAUDE.md"),
        mcp_global_path=home / ".claude.json",
        mcp_project_relative_path=Path(".mcp.json"),
        hook_global_path=home / ".claude" / "settings.json",
        hook_project_relative_path=Path(".claude") / "settings.json",
    )
