from pathlib import Path

import pytest
import typer

from helix.cli import cmd_sync_clone, cmd_sync_init, cmd_sync_pull, cmd_sync_push
from helix.core import Brain, Settings, SyncError


def test_cmd_sync_init_echoes_configured_remote(
    remote_repository: str, capsys: pytest.CaptureFixture[str]
) -> None:
    cmd_sync_init(remote_url=remote_repository)
    captured = capsys.readouterr()
    assert f"Configured 'origin' -> {remote_repository}" in captured.out


def test_cmd_sync_init_reports_git_failures(
    monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    def _raise(_remote_url: str) -> None:
        raise SyncError("git init failed")

    monkeypatch.setattr("helix.cli.commands.sync_init", _raise)
    with pytest.raises(typer.Exit) as exc_info:
        cmd_sync_init(remote_url="https://example.invalid/repo.git")
    assert exc_info.value.exit_code == 1
    assert "git init failed" in capsys.readouterr().err


@pytest.mark.usefixtures("_remember_convention")
def test_cmd_sync_push_echoes_success(
    remote_repository: str, capsys: pytest.CaptureFixture[str]
) -> None:
    cmd_sync_init(remote_url=remote_repository)
    capsys.readouterr()
    cmd_sync_push(message="Update conventions")
    captured = capsys.readouterr()
    assert "Pushed conventions to origin." in captured.out


def test_cmd_sync_push_without_init_exits_with_error(
    capsys: pytest.CaptureFixture[str],
) -> None:
    with pytest.raises(typer.Exit) as exc_info:
        cmd_sync_push(message="Update conventions")
    assert exc_info.value.exit_code == 1
    captured = capsys.readouterr()
    assert "sync init" in captured.err


@pytest.mark.usefixtures("_remember_convention")
def test_cmd_sync_clone_reports_merge_summary(
    remote_repository: str, tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    cmd_sync_init(remote_url=remote_repository)
    cmd_sync_push(message="Update conventions")
    capsys.readouterr()

    Settings.HOME_DIRECTORY = tmp_path / "other-host"
    fresh_brain = Brain()
    assert not fresh_brain.is_initialized

    cmd_sync_clone(remote_url=remote_repository)
    captured = capsys.readouterr()
    assert "conv-a.md" in captured.out
    assert (fresh_brain.conventions / "conv-a.md").exists()


def test_cmd_sync_pull_without_init_exits_with_error(
    capsys: pytest.CaptureFixture[str],
) -> None:
    with pytest.raises(typer.Exit) as exc_info:
        cmd_sync_pull()
    assert exc_info.value.exit_code == 1
    captured = capsys.readouterr()
    assert "sync init" in captured.err


@pytest.mark.usefixtures("_remember_convention")
def test_cmd_sync_pull_echoes_merge_summary(
    remote_repository: str, tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    cmd_sync_init(remote_url=remote_repository)
    cmd_sync_push(message="Update conventions")

    Settings.HOME_DIRECTORY = tmp_path / "other-host"
    cmd_sync_clone(remote_url=remote_repository)
    Brain().remember(name="conv-b", body="Body B.", tags=["typescript"])
    cmd_sync_push(message="Update conventions")

    Settings.HOME_DIRECTORY = tmp_path
    capsys.readouterr()
    cmd_sync_pull()
    captured = capsys.readouterr()
    assert "Pulled from origin:" in captured.out
    assert "conv-b.md" in captured.out


def test_cmd_sync_clone_reports_git_failures(
    monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    def _raise(_remote_url: str, strategy: object) -> None:
        raise SyncError("git clone failed")

    monkeypatch.setattr("helix.cli.commands.sync_clone", _raise)
    with pytest.raises(typer.Exit) as exc_info:
        cmd_sync_clone(remote_url="https://example.invalid/repo.git")
    assert exc_info.value.exit_code == 1
    assert "git clone failed" in capsys.readouterr().err
