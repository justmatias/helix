from pathlib import Path

from helix.core.installer.models import Client
from helix.core.settings import Settings


def cursor() -> Client:
    home = Settings.HOME_DIRECTORY
    return Client(
        key="cursor",
        name="Cursor",
        global_path=home / ".cursor" / "rules" / "helix.mdc",
        project_relative_path=Path(".cursor") / "rules" / "helix.mdc",
        preamble="---\nalwaysApply: true\n---",
        detect_path=home / ".cursor",
        mcp_global_path=home / ".cursor" / "mcp.json",
        mcp_project_relative_path=Path(".cursor") / "mcp.json",
    )
