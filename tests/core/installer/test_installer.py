from pathlib import Path

import pytest

from helix.core import (
    END_MARKER,
    SNIPPET,
    START_MARKER,
    Client,
    Scope,
    clients,
    detect_installed_clients,
    detect_snippet_blocks,
    install,
    uninstall,
)


def test_install_creates_file_with_block(
    tmp_path: Path, claude_client: Client, claude_md: Path
) -> None:
    path = install(claude_client, Scope.PROJECT, tmp_path)
    text = path.read_text()
    assert path == claude_md
    assert START_MARKER in text
    assert END_MARKER in text
    assert SNIPPET.strip() in text


@pytest.mark.usefixtures("_write_existing_claude_md")
def test_install_appends_to_existing_file(
    tmp_path: Path, claude_client: Client, claude_md: Path, existing_content: str
) -> None:
    install(claude_client, Scope.PROJECT, tmp_path)
    text = claude_md.read_text()
    assert existing_content in text
    assert text.count(START_MARKER) == 1


def test_install_is_idempotent(
    tmp_path: Path, claude_client: Client, claude_md: Path
) -> None:
    install(claude_client, Scope.PROJECT, tmp_path)
    install(claude_client, Scope.PROJECT, tmp_path)
    text = claude_md.read_text()
    assert text.count(START_MARKER) == 1
    assert text.count(END_MARKER) == 1


def test_install_global_uses_settings_home(
    tmp_path: Path, claude_client: Client, global_claude_md: Path
) -> None:
    path = install(claude_client, Scope.GLOBAL, tmp_path)
    assert path == global_claude_md
    assert path.exists()


@pytest.mark.usefixtures("_write_existing_claude_md")
def test_uninstall_removes_block_keeping_other_content(
    tmp_path: Path, claude_client: Client, claude_md: Path, existing_content: str
) -> None:
    install(claude_client, Scope.PROJECT, tmp_path)
    assert uninstall(claude_client, Scope.PROJECT, tmp_path)

    text = claude_md.read_text()
    assert START_MARKER not in text
    assert existing_content in text


def test_uninstall_deletes_file_when_only_block(
    tmp_path: Path, claude_client: Client, claude_md: Path
) -> None:
    install(claude_client, Scope.PROJECT, tmp_path)
    assert uninstall(claude_client, Scope.PROJECT, tmp_path)
    assert not claude_md.exists()


def test_uninstall_returns_false_when_missing(
    tmp_path: Path, claude_client: Client
) -> None:
    assert not uninstall(claude_client, Scope.PROJECT, tmp_path)


@pytest.mark.usefixtures("_write_existing_claude_md")
def test_uninstall_returns_false_when_no_block_in_existing_file(
    tmp_path: Path, claude_client: Client, claude_md: Path, existing_content: str
) -> None:
    assert not uninstall(claude_client, Scope.PROJECT, tmp_path)
    assert claude_md.read_text() == existing_content


@pytest.mark.usefixtures("_create_claude_global_directory")
def test_detect_installed_clients_finds_claude() -> None:
    detected = {client.key for client in detect_installed_clients()}
    assert "claude" in detected
    assert "cursor" not in detected


def test_clients_include_codex_and_opencode() -> None:
    keys = {client.key for client in clients()}
    assert {"claude", "cursor", "codex", "opencode"} == keys


def test_detect_snippet_blocks_lists_written_locations(
    tmp_path: Path, claude_client: Client
) -> None:
    install(claude_client, Scope.PROJECT, tmp_path)
    install(claude_client, Scope.GLOBAL, tmp_path)
    blocks = detect_snippet_blocks(tmp_path)
    scopes = {block.scope for block in blocks}
    assert scopes == {Scope.PROJECT, Scope.GLOBAL}


@pytest.mark.usefixtures("_write_existing_claude_md")
def test_detect_snippet_blocks_skips_files_without_marker(tmp_path: Path) -> None:
    assert not detect_snippet_blocks(tmp_path)
