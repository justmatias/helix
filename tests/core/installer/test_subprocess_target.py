import json
import subprocess
from collections.abc import Callable
from pathlib import Path

import pytest

from helix.core.installer import (
    JSON_MCP_FORMAT,
    Client,
    McpConfigTarget,
    Scope,
    SubprocessInstallTarget,
)

ADD_COMMAND = ["testcli", "mcp", "add", "-s", "user", "helix", "--", "helix", "serve"]
REMOVE_COMMAND = ["testcli", "mcp", "remove", "-s", "user", "helix"]


@pytest.fixture
def subprocess_target(tmp_path: Path) -> SubprocessInstallTarget:
    return SubprocessInstallTarget(
        fallback=McpConfigTarget(
            global_path=tmp_path / ".testclient" / "mcp.json",
            project_relative_path=Path(".testclient") / "mcp.json",
            config_format=JSON_MCP_FORMAT,
        ),
        subprocess_scope=Scope.GLOBAL,
        add_command=ADD_COMMAND,
        remove_command=REMOVE_COMMAND,
    )


def _recording_run(calls: list[list[str]]) -> Callable[..., subprocess.CompletedProcess]:
    def _run(cmd: list[str], **_kwargs: object) -> subprocess.CompletedProcess:
        calls.append(cmd)
        return subprocess.CompletedProcess(cmd, 0)

    return _run


def test_install_global_uses_cli_when_available(
    tmp_path: Path,
    subprocess_target: SubprocessInstallTarget,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    calls: list[list[str]] = []
    monkeypatch.setattr(
        "helix.core.installer.targets.shutil.which", lambda _name: "/usr/bin/testcli"
    )
    monkeypatch.setattr("helix.core.installer.targets.subprocess.run", _recording_run(calls))

    result = subprocess_target.install(Scope.GLOBAL, tmp_path)

    assert result == subprocess_target.fallback.global_path
    assert calls == [ADD_COMMAND]
    assert subprocess_target.fallback.global_path is not None
    assert not subprocess_target.fallback.global_path.exists()


def test_install_falls_back_to_file_without_cli(
    tmp_path: Path,
    subprocess_target: SubprocessInstallTarget,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr("helix.core.installer.targets.shutil.which", lambda _name: None)
    path = subprocess_target.install(Scope.GLOBAL, tmp_path)
    assert path is not None and path.exists()
    data = json.loads(path.read_text())
    assert data["mcpServers"]["helix"] == {"command": "helix", "args": ["serve"]}


def test_install_project_scope_never_uses_cli(
    tmp_path: Path,
    subprocess_target: SubprocessInstallTarget,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    calls: list[list[str]] = []
    monkeypatch.setattr(
        "helix.core.installer.targets.shutil.which", lambda _name: "/usr/bin/testcli"
    )
    monkeypatch.setattr("helix.core.installer.targets.subprocess.run", _recording_run(calls))
    path = subprocess_target.install(Scope.PROJECT, tmp_path)
    assert not calls
    assert path is not None and path.exists()


def test_uninstall_global_uses_cli_when_available(
    tmp_path: Path,
    subprocess_target: SubprocessInstallTarget,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    calls: list[list[str]] = []
    monkeypatch.setattr(
        "helix.core.installer.targets.shutil.which", lambda _name: "/usr/bin/testcli"
    )
    monkeypatch.setattr("helix.core.installer.targets.subprocess.run", _recording_run(calls))

    assert subprocess_target.uninstall(Scope.GLOBAL, tmp_path)
    assert calls == [REMOVE_COMMAND]


def test_uninstall_reports_cli_failure(
    tmp_path: Path,
    subprocess_target: SubprocessInstallTarget,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(
        "helix.core.installer.targets.shutil.which", lambda _name: "/usr/bin/testcli"
    )
    monkeypatch.setattr(
        "helix.core.installer.targets.subprocess.run",
        lambda cmd, **_kwargs: subprocess.CompletedProcess(cmd, 1),
    )
    assert not subprocess_target.uninstall(Scope.GLOBAL, tmp_path)


def test_claude_client_wires_real_subprocess_target(claude_client: Client) -> None:
    subprocess_target = next(
        t for t in claude_client.extra_targets if isinstance(t, SubprocessInstallTarget)
    )
    assert subprocess_target.add_command[0] == "claude"
    assert subprocess_target.subprocess_scope == Scope.GLOBAL
