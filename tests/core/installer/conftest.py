from pathlib import Path

import pytest

from helix.core import clients
from helix.core.installer import (
    JSON_MCP_FORMAT,
    OPENCODE_MCP_FORMAT,
    TOML_MCP_FORMAT,
    Client,
    HookTarget,
    McpConfigTarget,
    Scope,
)


@pytest.fixture
def claude_client() -> Client:
    return next(client for client in clients() if client.key == "claude")


@pytest.fixture
def cursor_client() -> Client:
    return next(client for client in clients() if client.key == "cursor")


@pytest.fixture
def hook_target(claude_client: Client) -> HookTarget:
    """Claude Code — the only client with a SessionStart hook target."""
    return next(t for t in claude_client.extra_targets if isinstance(t, HookTarget))


@pytest.fixture
def json_mcp_target(tmp_path: Path) -> McpConfigTarget:
    return McpConfigTarget(
        global_path=tmp_path / ".testclient" / "mcp.json",
        project_relative_path=Path(".testclient") / "mcp.json",
        config_format=JSON_MCP_FORMAT,
    )


@pytest.fixture
def toml_mcp_target(tmp_path: Path) -> McpConfigTarget:
    return McpConfigTarget(
        global_path=tmp_path / ".testclient" / "config.toml",
        project_relative_path=None,
        config_format=TOML_MCP_FORMAT,
    )


@pytest.fixture
def opencode_mcp_target(tmp_path: Path) -> McpConfigTarget:
    return McpConfigTarget(
        global_path=tmp_path / ".testclient" / "opencode.json",
        project_relative_path=Path(".testclient") / "opencode.json",
        config_format=OPENCODE_MCP_FORMAT,
    )


@pytest.fixture
def claude_md(tmp_path: Path) -> Path:
    return tmp_path / "CLAUDE.md"


@pytest.fixture
def global_claude_md(tmp_path: Path) -> Path:
    return tmp_path / ".claude" / "CLAUDE.md"


@pytest.fixture
def existing_content() -> str:
    return "# Project Notes\n\nExisting content.\n"


@pytest.fixture
def _write_existing_claude_md(claude_md: Path, existing_content: str) -> None:
    claude_md.write_text(existing_content)


@pytest.fixture
def _create_claude_global_directory(tmp_path: Path) -> None:
    (tmp_path / ".claude").mkdir()


@pytest.fixture
def _create_cursor_global_directory(tmp_path: Path) -> None:
    (tmp_path / ".cursor").mkdir()


@pytest.fixture
def hook_global_path(hook_target: HookTarget, tmp_path: Path) -> Path:
    path = hook_target.path_for(Scope.GLOBAL, tmp_path)
    assert path is not None
    path.parent.mkdir(parents=True, exist_ok=True)
    return path
