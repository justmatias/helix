import json
from pathlib import Path

import pytest

from helix.core.installer import (
    HOOK_COMMAND,
    HOOK_EVENT,
    HookTarget,
    InvalidConfigError,
    Scope,
)


def _commands(path: Path) -> list[str]:
    data = json.loads(path.read_text())
    return [
        hook["command"]
        for entry in data["hooks"][HOOK_EVENT]
        for hook in entry["hooks"]
    ]


def test_install_creates_settings_file(
    hook_target: HookTarget, hook_global_path: Path
) -> None:
    assert hook_target.install(Scope.GLOBAL, Path.cwd()) == hook_global_path
    assert _commands(hook_global_path) == [HOOK_COMMAND]


def test_install_preserves_existing_settings(
    hook_target: HookTarget, hook_global_path: Path
) -> None:
    hook_global_path.write_text(json.dumps({"theme": "dark"}))
    hook_target.install(Scope.GLOBAL, Path.cwd())
    data = json.loads(hook_global_path.read_text())
    assert data["theme"] == "dark"
    assert _commands(hook_global_path) == [HOOK_COMMAND]


def test_install_keeps_foreign_session_start_entries(
    hook_target: HookTarget, hook_global_path: Path
) -> None:
    hook_global_path.write_text(
        json.dumps(
            {"hooks": {HOOK_EVENT: [{"hooks": [{"type": "command", "command": "echo hi"}]}]}}
        )
    )
    hook_target.install(Scope.GLOBAL, Path.cwd())
    assert _commands(hook_global_path) == ["echo hi", HOOK_COMMAND]


def test_install_is_idempotent_in_content(
    hook_target: HookTarget, hook_global_path: Path
) -> None:
    hook_target.install(Scope.GLOBAL, Path.cwd())
    assert hook_target.install(Scope.GLOBAL, Path.cwd()) == hook_global_path
    assert _commands(hook_global_path) == [HOOK_COMMAND]


def test_install_returns_none_without_hook_path(tmp_path: Path) -> None:
    no_hook = HookTarget(global_path=None, project_relative_path=None)
    assert no_hook.install(Scope.GLOBAL, tmp_path) is None
    assert no_hook.install(Scope.PROJECT, tmp_path) is None


def test_install_project_scope(hook_target: HookTarget, tmp_path: Path) -> None:
    path = hook_target.install(Scope.PROJECT, tmp_path)
    assert path == tmp_path / ".claude" / "settings.json"
    assert path is not None
    assert _commands(path) == [HOOK_COMMAND]


def test_uninstall_deletes_file_when_empty(
    hook_target: HookTarget, hook_global_path: Path
) -> None:
    hook_target.install(Scope.GLOBAL, Path.cwd())
    assert hook_target.uninstall(Scope.GLOBAL, Path.cwd())
    assert not hook_global_path.exists()


def test_uninstall_keeps_other_settings(
    hook_target: HookTarget, hook_global_path: Path
) -> None:
    hook_global_path.write_text(json.dumps({"theme": "dark"}))
    hook_target.install(Scope.GLOBAL, Path.cwd())
    hook_target.uninstall(Scope.GLOBAL, Path.cwd())
    data = json.loads(hook_global_path.read_text())
    assert data == {"theme": "dark"}


def test_uninstall_keeps_foreign_entries(
    hook_target: HookTarget, hook_global_path: Path
) -> None:
    hook_target.install(Scope.GLOBAL, Path.cwd())
    data = json.loads(hook_global_path.read_text())
    data["hooks"][HOOK_EVENT].append({"hooks": [{"type": "command", "command": "echo hi"}]})
    hook_global_path.write_text(json.dumps(data))
    assert hook_target.uninstall(Scope.GLOBAL, Path.cwd())
    assert _commands(hook_global_path) == ["echo hi"]


def test_uninstall_returns_false_when_absent(
    hook_target: HookTarget, hook_global_path: Path
) -> None:
    hook_global_path.write_text(json.dumps({"theme": "dark"}))
    assert not hook_target.uninstall(Scope.GLOBAL, Path.cwd())


def test_uninstall_returns_false_without_file(
    hook_target: HookTarget, tmp_path: Path
) -> None:
    assert not hook_target.uninstall(Scope.PROJECT, tmp_path)


def test_install_treats_empty_file_as_empty_settings(
    hook_target: HookTarget, hook_global_path: Path
) -> None:
    hook_global_path.write_text("")
    hook_target.install(Scope.GLOBAL, Path.cwd())
    assert _commands(hook_global_path) == [HOOK_COMMAND]


def test_uninstall_swallows_invalid_existing_settings(
    hook_target: HookTarget, hook_global_path: Path
) -> None:
    """InvalidConfigError is caught and logged inside the target, not raised —
    so the CLI loop no longer needs to guard each artifact type by hand."""
    hook_global_path.write_text("{not valid json")
    assert not hook_target.uninstall(Scope.GLOBAL, Path.cwd())
    assert hook_global_path.read_text() == "{not valid json"


def test_merge_raises_on_invalid_existing_settings(hook_target: HookTarget) -> None:
    with pytest.raises(InvalidConfigError, match="not valid JSON"):
        hook_target.merge("{not valid json", Path("settings.json"))
