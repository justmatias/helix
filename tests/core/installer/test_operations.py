import json
from pathlib import Path

import pytest

from helix.core.installer import (
    JSON_MCP_FORMAT,
    Client,
    HookTarget,
    McpConfigTarget,
    Scope,
    SnippetTarget,
    clients,
    detect_installed_clients,
    detect_snippet_blocks,
)


def _install_all(client: Client, scope: Scope, project_root: Path) -> None:
    for target in client.all_targets:
        target.install(scope, project_root)


def test_clients_include_claude_cursor_codex_and_opencode() -> None:
    keys = {client.key for client in clients()}
    assert {"claude", "cursor", "codex", "opencode"} == keys


@pytest.mark.usefixtures("_create_claude_global_directory")
def test_detect_installed_clients_finds_claude() -> None:
    detected = {client.key for client in detect_installed_clients()}
    assert "claude" in detected
    assert "cursor" not in detected


@pytest.mark.usefixtures("_create_cursor_global_directory")
def test_detect_installed_clients_finds_cursor_via_dot_cursor_dir() -> None:
    detected = {client.key for client in detect_installed_clients()}
    assert "cursor" in detected


def test_detect_snippet_blocks_lists_written_locations(
    tmp_path: Path, claude_client: Client
) -> None:
    _install_all(claude_client, Scope.PROJECT, tmp_path)
    _install_all(claude_client, Scope.GLOBAL, tmp_path)
    blocks = detect_snippet_blocks(tmp_path)
    scopes = {block.scope for block in blocks if block.client.key == "claude"}
    assert scopes == {Scope.PROJECT, Scope.GLOBAL}


@pytest.mark.usefixtures("_write_existing_claude_md")
def test_detect_snippet_blocks_skips_files_without_marker(tmp_path: Path) -> None:
    assert not detect_snippet_blocks(tmp_path)


def test_detect_snippet_blocks_finds_mcp_only_leftover(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    mcp_only_client = Client(
        key="test-json",
        name="Test JSON",
        snippet=SnippetTarget(
            global_path=tmp_path / ".testclient" / "AGENTS.md",
            project_relative_path=Path("AGENTS.md"),
        ),
        extra_targets=[
            McpConfigTarget(
                global_path=tmp_path / ".testclient" / "mcp.json",
                project_relative_path=Path(".testclient") / "mcp.json",
                config_format=JSON_MCP_FORMAT,
            )
        ],
    )
    mcp_path = mcp_only_client.extra_targets[0].path_for(Scope.PROJECT, tmp_path)
    assert mcp_path is not None
    mcp_path.parent.mkdir(parents=True, exist_ok=True)
    mcp_path.write_text(
        json.dumps({"mcpServers": {"helix": {"command": "helix", "args": ["serve"]}}})
    )
    monkeypatch.setattr(
        "helix.core.installer.operations.clients", lambda: [mcp_only_client]
    )

    blocks = [
        block for block in detect_snippet_blocks(tmp_path) if block.scope == Scope.PROJECT
    ]
    assert blocks
    assert blocks[0].path == mcp_path


def test_detect_snippet_blocks_finds_hook_only_leftover(
    tmp_path: Path,
    claude_client: Client,
    hook_global_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    hook_target = next(t for t in claude_client.extra_targets if isinstance(t, HookTarget))
    hook_global_path.write_text(
        json.dumps(
            {"hooks": {"SessionStart": [{"hooks": [{"command": "helix list"}]}]}}
        )
    )
    monkeypatch.setattr(
        "helix.core.installer.operations.clients", lambda: [claude_client]
    )

    blocks = [
        block for block in detect_snippet_blocks(tmp_path) if block.scope == Scope.GLOBAL
    ]
    assert blocks
    assert blocks[0].path == hook_target.path_for(Scope.GLOBAL, tmp_path)
