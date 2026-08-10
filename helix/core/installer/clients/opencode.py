from pathlib import Path

from helix.core.settings import Settings

from ..models import Client


def opencode() -> Client:
    home = Settings.HOME_DIRECTORY
    return Client(
        key="opencode",
        name="Opencode",
        global_path=home / ".config" / "opencode" / "AGENTS.md",
        project_relative_path=Path("AGENTS.md"),
        mcp_global_path=home / ".config" / "opencode" / "opencode.json",
        mcp_project_relative_path=Path("opencode.json"),
    )
