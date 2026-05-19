from collections.abc import Iterator
from pathlib import Path
from typing import Any

import pytest
import typer

from helix.cli import (
    cmd_forget,
    cmd_install,
    cmd_list,
    cmd_recall,
    cmd_remember,
    cmd_uninstall,
)
from helix.core import START_MARKER, Brain, clients, install
from helix.core.installer.models import Scope


def _answers(monkeypatch: pytest.MonkeyPatch, *values: Any) -> None:
    """Feed ``typer.prompt`` a fixed sequence of answers."""
    it: Iterator[Any] = iter(values)
    monkeypatch.setattr(typer, "prompt", lambda *a, **k: next(it))


def test_cmd_remember_creates_file_and_echoes(
    capsys: pytest.CaptureFixture[str],
) -> None:
    cmd_remember(
        body="Always use async.",
        name="my-conv",
        tags="python,async",
        applies_to=None,
    )
    captured = capsys.readouterr()
    assert "Saved as my-conv.md" in captured.out
    assert (Brain().conventions / "my-conv.md").exists()


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
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    monkeypatch.chdir(tmp_path)
    # Pick the first client (Claude Code), then scope 2 (project).
    _answers(monkeypatch, "1", 2)
    cmd_install()
    captured = capsys.readouterr()
    target = tmp_path / "CLAUDE.md"
    assert "Wrote helix block to" in captured.out
    assert target.exists()
    assert START_MARKER in target.read_text()


def test_cmd_install_no_detected_clients_lists_all(
    capsys: pytest.CaptureFixture[str],
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    monkeypatch.chdir(tmp_path)
    _answers(monkeypatch, "1", 2)
    cmd_install()
    captured = capsys.readouterr()
    assert "No client config directories found" in captured.out


def test_cmd_uninstall_removes_existing_block(
    capsys: pytest.CaptureFixture[str],
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    claude = next(c for c in clients() if c.key == "claude")
    install(claude, Scope.PROJECT, tmp_path)
    monkeypatch.chdir(tmp_path)
    _answers(monkeypatch, 1)
    cmd_uninstall()
    captured = capsys.readouterr()
    assert "Removed helix block from" in captured.out
    assert not (tmp_path / "CLAUDE.md").exists()


def test_cmd_uninstall_no_blocks_found(
    capsys: pytest.CaptureFixture[str],
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    monkeypatch.chdir(tmp_path)
    cmd_uninstall()
    captured = capsys.readouterr()
    assert "No helix blocks found." in captured.out
