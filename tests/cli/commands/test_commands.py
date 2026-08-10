import io
import json
from collections.abc import Callable
from pathlib import Path

import pytest
import typer

from helix.cli import (
    cmd_edit,
    cmd_forget,
    cmd_install,
    cmd_list,
    cmd_recall,
    cmd_remember,
    cmd_uninstall,
)
from helix.core import START_MARKER, Brain, Scope, Settings
from helix.core.installer.hooks import HOOK_EVENT


def test_cmd_remember_creates_file_and_echoes(
    capsys: pytest.CaptureFixture[str],
) -> None:
    cmd_remember(body="Always use async.", name="my-conv", tags="python,async")
    captured = capsys.readouterr()
    assert "Saved as my-conv.md" in captured.out
    assert (Brain().conventions / "my-conv.md").exists()


def test_cmd_remember_derives_name_from_body(
    capsys: pytest.CaptureFixture[str],
) -> None:
    cmd_remember(body="Prefer Pydantic v2 at boundaries.")
    captured = capsys.readouterr()
    assert "Saved as prefer-pydantic-v2-at-boundaries.md" in captured.out


def test_cmd_remember_suffixes_derived_name_on_collision(
    capsys: pytest.CaptureFixture[str],
) -> None:
    cmd_remember(body="Prefer Pydantic v2.")
    cmd_remember(body="Prefer Pydantic v2.")
    captured = capsys.readouterr()
    assert "Saved as prefer-pydantic-v2-2.md" in captured.out


def test_cmd_remember_reads_stdin(
    capsys: pytest.CaptureFixture[str], monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setattr("sys.stdin", io.StringIO("Piped convention body."))
    cmd_remember(body="-")
    captured = capsys.readouterr()
    assert "Saved as piped-convention-body.md" in captured.out


def test_cmd_remember_opens_editor_without_body(
    capsys: pytest.CaptureFixture[str], monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setattr(typer, "edit", lambda *a, **k: "Edited convention body.")
    cmd_remember()
    captured = capsys.readouterr()
    assert "Saved as edited-convention-body.md" in captured.out


def test_cmd_remember_empty_body_exits(
    capsys: pytest.CaptureFixture[str], monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setattr(typer, "edit", lambda *a, **k: None)
    with pytest.raises(typer.Exit) as exc:
        cmd_remember()
    assert exc.value.exit_code == 1
    assert "empty body" in capsys.readouterr().err


def test_cmd_list_empty(capsys: pytest.CaptureFixture[str]) -> None:
    cmd_list(tags=None)
    captured = capsys.readouterr()
    assert "No conventions found." in captured.out


def test_cmd_list_shows_entries(capsys: pytest.CaptureFixture[str]) -> None:
    Brain().remember(name="conv-a", body="Body A.", tags=["python"])
    cmd_list(tags=None)
    captured = capsys.readouterr()
    assert "conv-a" in captured.out


def test_cmd_list_filters_by_tags(capsys: pytest.CaptureFixture[str]) -> None:
    Brain().remember(name="conv-a", body="Body A.", tags=["python"])
    Brain().remember(name="conv-b", body="Body B.", tags=["typescript"])
    cmd_list(tags="python")
    captured = capsys.readouterr()
    assert "conv-a" in captured.out
    assert "conv-b" not in captured.out


def test_cmd_recall_no_match(capsys: pytest.CaptureFixture[str]) -> None:
    cmd_recall(query="nothing", tags=None)
    captured = capsys.readouterr()
    assert "No matches found." in captured.out


def test_cmd_recall_finds_match(capsys: pytest.CaptureFixture[str]) -> None:
    Brain().remember(name="pydantic", body="Prefer Pydantic v2.", tags=["python"])
    cmd_recall(query="Pydantic", tags=None)
    captured = capsys.readouterr()
    assert "pydantic" in captured.out


def test_cmd_recall_prints_full_body(capsys: pytest.CaptureFixture[str]) -> None:
    Brain().remember(
        name="pydantic", body="Prefer Pydantic v2.\nSecond line.", tags=["python"]
    )
    cmd_recall(query="Pydantic", tags=None)
    captured = capsys.readouterr()
    assert "## pydantic  [python]" in captured.out
    assert "Second line." in captured.out


def test_cmd_list_prints_header(capsys: pytest.CaptureFixture[str]) -> None:
    Brain().remember(name="conv-a", body="Body A.", tags=["python"])
    cmd_list(tags=None)
    assert "# Helix Convention Index" in capsys.readouterr().out


def test_cmd_edit_refreshes_index(
    capsys: pytest.CaptureFixture[str], monkeypatch: pytest.MonkeyPatch
) -> None:
    brain = Brain()
    brain.remember(name="editable", body="Old body.", tags=["python"])

    def _edit(filename: str) -> None:
        Path(filename).write_text(
            "---\nname: editable\ntags: [python]\n---\n\nNew body.\n"
        )

    monkeypatch.setattr(typer, "edit", _edit)
    cmd_edit(name="editable")
    assert "Updated editable.md" in capsys.readouterr().out
    assert "New body." in brain.index.read_text()


def test_cmd_edit_missing_exits(capsys: pytest.CaptureFixture[str]) -> None:
    with pytest.raises(typer.Exit) as exc:
        cmd_edit(name="nonexistent")
    assert exc.value.exit_code == 1
    assert "not found" in capsys.readouterr().err


def test_cmd_edit_warns_when_file_no_longer_parses(
    capsys: pytest.CaptureFixture[str], monkeypatch: pytest.MonkeyPatch
) -> None:
    Brain().remember(name="editable", body="Old body.", tags=["python"])
    monkeypatch.setattr(
        typer, "edit", lambda filename: Path(filename).write_text("broken\n")
    )
    cmd_edit(name="editable")
    assert "no longer parses" in capsys.readouterr().err


def test_cmd_forget_removes(capsys: pytest.CaptureFixture[str]) -> None:
    Brain().remember(name="to-delete", body="Body.", tags=["misc"])
    cmd_forget(name="to-delete")
    captured = capsys.readouterr()
    assert "Removed to-delete" in captured.out


def test_cmd_forget_missing_exits(capsys: pytest.CaptureFixture[str]) -> None:
    with pytest.raises(typer.Exit) as exc:
        cmd_forget(name="nonexistent")
    assert exc.value.exit_code == 1
    captured = capsys.readouterr()
    assert "not found" in captured.err


def test_cmd_install_writes_block_for_selected_client(
    capsys: pytest.CaptureFixture[str],
    set_answers: Callable[..., None],
    working_dir: Path,
) -> None:
    # Pick the first client (Claude Code), then scope 2 (project).
    set_answers("1", 2)
    cmd_install()
    captured = capsys.readouterr()
    target = working_dir / "CLAUDE.md"
    assert "Wrote helix block to" in captured.out
    assert target.exists()
    assert START_MARKER in target.read_text()


def test_cmd_install_no_detected_clients_lists_all(
    capsys: pytest.CaptureFixture[str],
    set_answers: Callable[..., None],
    working_dir: Path,
) -> None:
    set_answers("1", 2)
    cmd_install()
    captured = capsys.readouterr()
    assert "No client config directories found" in captured.out


def test_cmd_install_non_interactive_with_flags(
    capsys: pytest.CaptureFixture[str], working_dir: Path
) -> None:
    cmd_install(client=["claude"], scope=Scope.PROJECT, yes=True)
    captured = capsys.readouterr()
    assert START_MARKER in (working_dir / "CLAUDE.md").read_text()
    assert "helix" in json.loads((working_dir / ".mcp.json").read_text())["mcpServers"]
    settings = json.loads((working_dir / ".claude" / "settings.json").read_text())
    assert settings["hooks"][HOOK_EVENT]
    assert "Restart your client" in captured.out


@pytest.mark.usefixtures("working_dir")
def test_cmd_install_rejects_unknown_client(
    capsys: pytest.CaptureFixture[str],
) -> None:
    with pytest.raises(typer.Exit) as exc:
        cmd_install(client=["nope"], scope=Scope.PROJECT, yes=True)
    assert exc.value.exit_code == 1
    assert "Unknown client(s): nope" in capsys.readouterr().err


@pytest.mark.usefixtures("working_dir", "_create_claude_directory")
def test_cmd_install_yes_defaults_to_all_detected_and_global(
    capsys: pytest.CaptureFixture[str],
) -> None:
    cmd_install(yes=True)
    captured = capsys.readouterr()
    assert "No client config directories found" not in captured.out
    assert START_MARKER in (Settings.HOME_DIRECTORY / ".claude" / "CLAUDE.md").read_text()


def test_cmd_uninstall_yes_reverts_everything_install_wrote(
    capsys: pytest.CaptureFixture[str], working_dir: Path
) -> None:
    cmd_install(client=["claude"], scope=Scope.PROJECT, yes=True)
    capsys.readouterr()
    cmd_uninstall(yes=True)
    captured = capsys.readouterr()
    assert "Removed helix block from" in captured.out
    assert "Removed MCP server config" in captured.out
    assert "Removed SessionStart hook" in captured.out
    assert not (working_dir / "CLAUDE.md").exists()
    assert not (working_dir / ".mcp.json").exists()
    assert not (working_dir / ".claude" / "settings.json").exists()


@pytest.mark.usefixtures("_install_claude_client")
def test_cmd_uninstall_removes_existing_block(
    capsys: pytest.CaptureFixture[str],
    set_answers: Callable[..., None],
    working_dir: Path,
) -> None:
    set_answers("1")
    cmd_uninstall()
    captured = capsys.readouterr()
    assert "Removed helix block from" in captured.out
    assert not (working_dir / "CLAUDE.md").exists()


@pytest.mark.usefixtures("working_dir")
def test_cmd_uninstall_no_blocks_found(
    capsys: pytest.CaptureFixture[str],
) -> None:
    cmd_uninstall()
    captured = capsys.readouterr()
    assert "No helix blocks found." in captured.out


@pytest.mark.usefixtures("_install_claude_client")
def test_cmd_uninstall_reports_when_nothing_removed(
    capsys: pytest.CaptureFixture[str],
    set_answers: Callable[..., None],
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    set_answers("1")
    monkeypatch.setattr("helix.cli.install.uninstall", lambda *a, **k: False)
    with pytest.raises(typer.Exit) as exc_info:
        cmd_uninstall()
    assert exc_info.value.exit_code == 1
    captured = capsys.readouterr()
    assert "Nothing to remove from" in captured.err
