import json
from collections.abc import Callable
from pathlib import Path

from helix.core import (
    HOOK_COMMAND,
    HOOK_EVENT,
    Client,
    Scope,
    install_hook,
    uninstall_hook,
)


def _commands(path: Path) -> list[str]:
    data = json.loads(path.read_text())
    return [
        hook["command"]
        for entry in data["hooks"][HOOK_EVENT]
        for hook in entry["hooks"]
    ]


def test_install_hook_creates_settings_file(
    install_hook_globally: Callable[[], Path | None], hook_global_path: Path
) -> None:
    assert install_hook_globally() == hook_global_path
    assert _commands(hook_global_path) == [HOOK_COMMAND]


def test_install_hook_preserves_existing_settings(
    install_hook_globally: Callable[[], Path | None], hook_global_path: Path
) -> None:
    hook_global_path.write_text(json.dumps({"theme": "dark"}))
    install_hook_globally()
    data = json.loads(hook_global_path.read_text())
    assert data["theme"] == "dark"
    assert _commands(hook_global_path) == [HOOK_COMMAND]


def test_install_hook_keeps_foreign_session_start_entries(
    install_hook_globally: Callable[[], Path | None], hook_global_path: Path
) -> None:
    hook_global_path.write_text(
        json.dumps({
            "hooks": {
                HOOK_EVENT: [{"hooks": [{"type": "command", "command": "echo hi"}]}]
            }
        })
    )
    install_hook_globally()
    assert _commands(hook_global_path) == ["echo hi", HOOK_COMMAND]


def test_install_hook_is_idempotent(
    install_hook_globally: Callable[[], Path | None], hook_global_path: Path
) -> None:
    install_hook_globally()
    assert install_hook_globally() is None
    assert _commands(hook_global_path) == [HOOK_COMMAND]


def test_install_hook_returns_none_without_hook_path(
    json_mcp_client: Client, tmp_path: Path
) -> None:
    assert install_hook(json_mcp_client, Scope.GLOBAL, tmp_path) is None
    assert install_hook(json_mcp_client, Scope.PROJECT, tmp_path) is None


def test_install_hook_project_scope(hook_client: Client, tmp_path: Path) -> None:
    path = install_hook(hook_client, Scope.PROJECT, tmp_path)
    assert path == tmp_path / ".claude" / "settings.json"
    assert path is not None
    assert _commands(path) == [HOOK_COMMAND]


def test_uninstall_hook_deletes_file_when_empty(
    install_hook_globally: Callable[[], Path | None],
    uninstall_hook_globally: Callable[[], bool],
    hook_global_path: Path,
) -> None:
    install_hook_globally()
    assert uninstall_hook_globally()
    assert not hook_global_path.exists()


def test_uninstall_hook_keeps_other_settings(
    install_hook_globally: Callable[[], Path | None],
    uninstall_hook_globally: Callable[[], bool],
    hook_global_path: Path,
) -> None:
    hook_global_path.write_text(json.dumps({"theme": "dark"}))
    install_hook_globally()
    uninstall_hook_globally()
    data = json.loads(hook_global_path.read_text())
    assert data == {"theme": "dark"}


def test_uninstall_hook_keeps_foreign_entries(
    install_hook_globally: Callable[[], Path | None],
    uninstall_hook_globally: Callable[[], bool],
    hook_global_path: Path,
) -> None:
    install_hook_globally()
    data = json.loads(hook_global_path.read_text())
    data["hooks"][HOOK_EVENT].append({
        "hooks": [{"type": "command", "command": "echo hi"}]
    })
    hook_global_path.write_text(json.dumps(data))
    assert uninstall_hook_globally()
    assert _commands(hook_global_path) == ["echo hi"]


def test_uninstall_hook_returns_false_when_absent(
    uninstall_hook_globally: Callable[[], bool], hook_global_path: Path
) -> None:
    hook_global_path.write_text(json.dumps({"theme": "dark"}))
    assert not uninstall_hook_globally()


def test_uninstall_hook_returns_false_without_file(
    hook_client: Client, tmp_path: Path
) -> None:
    assert not uninstall_hook(hook_client, Scope.PROJECT, tmp_path)
