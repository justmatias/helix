import subprocess
import sys

import pytest

from helix.core import updater
from helix.core.updater import PACKAGE_NAME, update, update_command


@pytest.fixture
def _uv_available(monkeypatch: pytest.MonkeyPatch) -> None:
    """Make ``shutil.which('uv')`` resolve, as if uv were on PATH."""
    monkeypatch.setattr(updater.shutil, "which", lambda name: f"/usr/bin/{name}")


@pytest.fixture
def _uv_unavailable(monkeypatch: pytest.MonkeyPatch) -> None:
    """Make ``shutil.which('uv')`` resolve to nothing."""
    monkeypatch.setattr(updater.shutil, "which", lambda _name: None)


@pytest.fixture
def uv_tool_list_calls(monkeypatch: pytest.MonkeyPatch) -> list[list[str]]:
    """Record every argv passed to ``subprocess.run`` and answer as ``uv tool list``."""
    calls: list[list[str]] = []

    def _run(cmd: list[str], **_kwargs: object) -> subprocess.CompletedProcess[str]:
        calls.append(cmd)
        stdout = f"{PACKAGE_NAME} v1.0.0\nother-tool v2.0.0\n"
        return subprocess.CompletedProcess(cmd, 0, stdout=stdout)

    monkeypatch.setattr(updater.subprocess, "run", _run)
    return calls


@pytest.fixture
def uv_tool_list_without_helix(monkeypatch: pytest.MonkeyPatch) -> None:
    """Make ``uv tool list`` report no managed tools at all."""
    monkeypatch.setattr(
        updater.subprocess,
        "run",
        lambda cmd, **_kwargs: subprocess.CompletedProcess(cmd, 0, stdout=""),
    )


@pytest.mark.usefixtures("_uv_available")
def test_update_command_prefers_uv_tool_upgrade_when_managed_by_uv(
    uv_tool_list_calls: list[list[str]],
) -> None:
    assert update_command() == ["uv", "tool", "upgrade", PACKAGE_NAME]
    assert uv_tool_list_calls == [["uv", "tool", "list"]]


@pytest.mark.usefixtures("_uv_available", "uv_tool_list_without_helix")
def test_update_command_falls_back_to_pip_when_uv_does_not_manage_helix() -> None:
    assert update_command() == [sys.executable, "-m", "pip", "install", "--upgrade", PACKAGE_NAME]


@pytest.mark.usefixtures("_uv_unavailable")
def test_update_command_falls_back_to_pip_when_uv_is_not_on_path() -> None:
    assert update_command() == [sys.executable, "-m", "pip", "install", "--upgrade", PACKAGE_NAME]


@pytest.mark.usefixtures("_uv_unavailable")
def test_update_runs_the_resolved_command(monkeypatch: pytest.MonkeyPatch) -> None:
    calls: list[list[str]] = []

    def _run(cmd: list[str], **_kwargs: object) -> subprocess.CompletedProcess[str]:
        calls.append(cmd)
        return subprocess.CompletedProcess(cmd, 0)

    monkeypatch.setattr(updater.subprocess, "run", _run)
    result = update()
    assert result.returncode == 0
    assert calls == [[sys.executable, "-m", "pip", "install", "--upgrade", PACKAGE_NAME]]
