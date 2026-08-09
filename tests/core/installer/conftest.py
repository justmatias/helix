from collections.abc import Callable
from pathlib import Path

import pytest

from helix.core import (
    Client,
    McpConfigFormat,
    Scope,
    clients,
    install_hook,
    uninstall_hook,
)


@pytest.fixture
def claude_client() -> Client:
    return next(client for client in clients() if client.key == "claude")


@pytest.fixture
def cursor_client() -> Client:
    return next(client for client in clients() if client.key == "cursor")


@pytest.fixture
def json_mcp_client(tmp_path: Path) -> Client:
    return Client(
        key="test-json",
        name="Test JSON",
        global_path=tmp_path / ".testclient" / "AGENTS.md",
        project_relative_path=Path("AGENTS.md"),
        mcp_global_path=tmp_path / ".testclient" / "mcp.json",
        mcp_project_relative_path=Path(".testclient") / "mcp.json",
    )


@pytest.fixture
def toml_mcp_client(tmp_path: Path) -> Client:
    return Client(
        key="test-toml",
        name="Test TOML",
        global_path=tmp_path / ".testclient" / "AGENTS.md",
        project_relative_path=Path("AGENTS.md"),
        mcp_global_path=tmp_path / ".testclient" / "config.toml",
        mcp_format=McpConfigFormat.TOML,
    )


@pytest.fixture
def opencode_mcp_client(tmp_path: Path) -> Client:
    return Client(
        key="test-opencode",
        name="Test Opencode",
        global_path=tmp_path / ".testclient" / "AGENTS.md",
        project_relative_path=Path("AGENTS.md"),
        mcp_global_path=tmp_path / ".testclient" / "opencode.json",
        mcp_project_relative_path=Path(".testclient") / "opencode.json",
        mcp_format=McpConfigFormat.OPENCODE,
    )


@pytest.fixture
def json_mcp_project_path(json_mcp_client: Client, tmp_path: Path) -> Path:
    path = json_mcp_client.mcp_path_for(Scope.PROJECT, tmp_path)
    assert path is not None
    path.parent.mkdir(parents=True, exist_ok=True)
    return path


@pytest.fixture
def opencode_mcp_project_path(opencode_mcp_client: Client, tmp_path: Path) -> Path:
    path = opencode_mcp_client.mcp_path_for(Scope.PROJECT, tmp_path)
    assert path is not None
    path.parent.mkdir(parents=True, exist_ok=True)
    return path


@pytest.fixture
def toml_mcp_global_path(toml_mcp_client: Client, tmp_path: Path) -> Path:
    path = toml_mcp_client.mcp_path_for(Scope.GLOBAL, tmp_path)
    assert path is not None
    path.parent.mkdir(parents=True, exist_ok=True)
    return path


@pytest.fixture
def hook_client(claude_client: Client) -> Client:
    """Claude Code — the only client with SessionStart hook settings."""
    return claude_client


@pytest.fixture
def hook_global_path(hook_client: Client, tmp_path: Path) -> Path:
    path = hook_client.hook_path_for(Scope.GLOBAL, tmp_path)
    assert path is not None
    path.parent.mkdir(parents=True, exist_ok=True)
    return path


@pytest.fixture
def install_hook_globally(hook_client: Client) -> Callable[[], Path | None]:
    """Return a callable that installs ``hook_client``'s SessionStart hook globally."""
    return lambda: install_hook(hook_client, Scope.GLOBAL, Path.cwd())


@pytest.fixture
def uninstall_hook_globally(hook_client: Client) -> Callable[[], bool]:
    """Return a callable that removes ``hook_client``'s global SessionStart hook."""
    return lambda: uninstall_hook(hook_client, Scope.GLOBAL, Path.cwd())


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
