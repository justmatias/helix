from pathlib import Path

import pytest

from helix.core.installer import END_MARKER, SNIPPET, START_MARKER, Client, Scope


def test_install_creates_file_with_block(
    tmp_path: Path, claude_client: Client, claude_md: Path
) -> None:
    path = claude_client.snippet.install(Scope.PROJECT, tmp_path)
    text = path.read_text() if path else ""
    assert path == claude_md
    assert START_MARKER in text
    assert END_MARKER in text
    assert SNIPPET.strip() in text


@pytest.mark.usefixtures("_write_existing_claude_md")
def test_install_appends_to_existing_file(
    tmp_path: Path, claude_client: Client, claude_md: Path, existing_content: str
) -> None:
    claude_client.snippet.install(Scope.PROJECT, tmp_path)
    text = claude_md.read_text()
    assert existing_content in text
    assert text.count(START_MARKER) == 1


def test_install_is_idempotent(
    tmp_path: Path, claude_client: Client, claude_md: Path
) -> None:
    claude_client.snippet.install(Scope.PROJECT, tmp_path)
    claude_client.snippet.install(Scope.PROJECT, tmp_path)
    text = claude_md.read_text()
    assert text.count(START_MARKER) == 1
    assert text.count(END_MARKER) == 1


def test_install_global_uses_settings_home(
    tmp_path: Path, claude_client: Client, global_claude_md: Path
) -> None:
    path = claude_client.snippet.install(Scope.GLOBAL, tmp_path)
    assert path == global_claude_md
    assert path.exists()


@pytest.mark.usefixtures("_write_existing_claude_md")
def test_uninstall_removes_block_keeping_other_content(
    tmp_path: Path, claude_client: Client, claude_md: Path, existing_content: str
) -> None:
    claude_client.snippet.install(Scope.PROJECT, tmp_path)
    assert claude_client.snippet.uninstall(Scope.PROJECT, tmp_path)

    text = claude_md.read_text()
    assert START_MARKER not in text
    assert existing_content in text


def test_uninstall_deletes_file_when_only_block(
    tmp_path: Path, claude_client: Client, claude_md: Path
) -> None:
    claude_client.snippet.install(Scope.PROJECT, tmp_path)
    assert claude_client.snippet.uninstall(Scope.PROJECT, tmp_path)
    assert not claude_md.exists()


def test_uninstall_returns_false_when_missing(
    tmp_path: Path, claude_client: Client
) -> None:
    assert not claude_client.snippet.uninstall(Scope.PROJECT, tmp_path)


@pytest.mark.usefixtures("_write_existing_claude_md")
def test_uninstall_returns_false_when_no_block_in_existing_file(
    tmp_path: Path, claude_client: Client, claude_md: Path, existing_content: str
) -> None:
    assert not claude_client.snippet.uninstall(Scope.PROJECT, tmp_path)
    assert claude_md.read_text() == existing_content


def test_cursor_install_includes_frontmatter(
    tmp_path: Path, cursor_client: Client
) -> None:
    path = cursor_client.snippet.install(Scope.PROJECT, tmp_path)
    text = path.read_text() if path else ""
    assert text.startswith("---\nalwaysApply: true\n---")
    assert START_MARKER in text


def test_cursor_install_preserves_existing_frontmatter(
    tmp_path: Path, cursor_client: Client
) -> None:
    mdc_path = cursor_client.snippet.path_for(Scope.PROJECT, tmp_path)
    mdc_path.parent.mkdir(parents=True, exist_ok=True)
    existing = "---\nalwaysApply: true\n---\n\nSome existing content.\n"
    mdc_path.write_text(existing)

    cursor_client.snippet.install(Scope.PROJECT, tmp_path)
    text = mdc_path.read_text()
    assert text.count("---\nalwaysApply: true\n---") == 1
    assert "Some existing content." in text
    assert START_MARKER in text
