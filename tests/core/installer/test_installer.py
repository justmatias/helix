from pathlib import Path

import pytest

from helix.core.installer import (
    END_MARKER,
    SNIPPET,
    START_MARKER,
    clients,
    detect_installed_blocks,
    detect_installed_clients,
    install,
    uninstall,
)


@pytest.fixture
def claude_client():
    return next(c for c in clients() if c.key == "claude")


def test_install_creates_file_with_block(tmp_path: Path, claude_client) -> None:
    path = install(claude_client, "project", tmp_path)
    text = path.read_text()
    assert path == tmp_path / "CLAUDE.md"
    assert START_MARKER in text
    assert END_MARKER in text
    assert SNIPPET.strip() in text


def test_install_appends_to_existing_file(tmp_path: Path, claude_client) -> None:
    target = tmp_path / "CLAUDE.md"
    target.write_text("# Project Notes\n\nExisting content.\n")
    install(claude_client, "project", tmp_path)
    text = target.read_text()
    assert "Existing content." in text
    assert text.count(START_MARKER) == 1


def test_install_is_idempotent(tmp_path: Path, claude_client) -> None:
    install(claude_client, "project", tmp_path)
    install(claude_client, "project", tmp_path)
    text = (tmp_path / "CLAUDE.md").read_text()
    assert text.count(START_MARKER) == 1
    assert text.count(END_MARKER) == 1


def test_install_global_uses_settings_home(tmp_path: Path, claude_client) -> None:
    path = install(claude_client, "global", tmp_path)
    assert path == tmp_path / ".claude" / "CLAUDE.md"
    assert path.exists()


def test_uninstall_removes_block_keeping_other_content(
    tmp_path: Path, claude_client
) -> None:
    target = tmp_path / "CLAUDE.md"
    target.write_text("# Notes\n\nKeep me.\n")
    install(claude_client, "project", tmp_path)
    assert uninstall(claude_client, "project", tmp_path) is True
    text = target.read_text()
    assert START_MARKER not in text
    assert "Keep me." in text


def test_uninstall_deletes_file_when_only_block(
    tmp_path: Path, claude_client
) -> None:
    install(claude_client, "project", tmp_path)
    assert uninstall(claude_client, "project", tmp_path) is True
    assert not (tmp_path / "CLAUDE.md").exists()


def test_uninstall_returns_false_when_missing(tmp_path: Path, claude_client) -> None:
    assert uninstall(claude_client, "project", tmp_path) is False


def test_detect_installed_clients_finds_claude(tmp_path: Path) -> None:
    (tmp_path / ".claude").mkdir()
    detected = {c.key for c in detect_installed_clients()}
    assert "claude" in detected
    assert "cursor" not in detected


def test_detect_installed_blocks_lists_written_locations(
    tmp_path: Path, claude_client
) -> None:
    install(claude_client, "project", tmp_path)
    install(claude_client, "global", tmp_path)
    blocks = detect_installed_blocks(tmp_path)
    scopes = {scope for _, scope in blocks}
    assert scopes == {"project", "global"}
