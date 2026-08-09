import json
from pathlib import Path

import pytest

from helix.core.installer import (
    TOML_END,
    TOML_START,
    Client,
    InvalidConfigError,
    McpConfigTarget,
    Scope,
    SubprocessInstallTarget,
    clients,
)


def test_claude_uses_subprocess_target_with_json_fallback(claude_client: Client) -> None:
    mcp_target = next(t for t in claude_client.extra_targets if isinstance(t, McpConfigTarget | SubprocessInstallTarget))
    assert isinstance(mcp_target, SubprocessInstallTarget)
    assert mcp_target.fallback.global_path is not None
    assert mcp_target.fallback.global_path.name == ".claude.json"
    assert mcp_target.fallback.project_relative_path == Path(".mcp.json")


def test_cursor_client_has_json_mcp_config() -> None:
    cursor = next(c for c in clients() if c.key == "cursor")
    mcp_target = next(t for t in cursor.extra_targets if isinstance(t, McpConfigTarget))
    assert mcp_target.global_path is not None
    assert mcp_target.global_path.name == "mcp.json"
    assert mcp_target.project_relative_path == Path(".cursor") / "mcp.json"


def test_codex_client_has_toml_mcp_config() -> None:
    codex = next(c for c in clients() if c.key == "codex")
    mcp_target = next(t for t in codex.extra_targets if isinstance(t, McpConfigTarget))
    assert mcp_target.global_path is not None
    assert mcp_target.global_path.name == "config.toml"
    assert mcp_target.project_relative_path is None


# --- JSON format ---


def test_install_json_creates_file(tmp_path: Path, json_mcp_target: McpConfigTarget) -> None:
    path = json_mcp_target.install(Scope.PROJECT, tmp_path)
    assert path is not None and path.exists()
    data = json.loads(path.read_text())
    assert data["mcpServers"]["helix"] == {"command": "helix", "args": ["serve"]}


def test_install_json_merges_into_existing(
    tmp_path: Path, json_mcp_target: McpConfigTarget
) -> None:
    path = json_mcp_target.path_for(Scope.PROJECT, tmp_path)
    assert path is not None
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps({"mcpServers": {"other": {"command": "other"}}}))

    json_mcp_target.install(Scope.PROJECT, tmp_path)
    data = json.loads(path.read_text())
    assert "other" in data["mcpServers"]
    assert data["mcpServers"]["helix"] == {"command": "helix", "args": ["serve"]}


def test_install_json_is_idempotent(
    tmp_path: Path, json_mcp_target: McpConfigTarget
) -> None:
    json_mcp_target.install(Scope.PROJECT, tmp_path)
    json_mcp_target.install(Scope.PROJECT, tmp_path)
    path = json_mcp_target.path_for(Scope.PROJECT, tmp_path)
    assert path is not None
    data = json.loads(path.read_text())
    assert list(data["mcpServers"].keys()).count("helix") == 1


def test_install_returns_none_for_missing_scope(
    tmp_path: Path, json_mcp_target: McpConfigTarget
) -> None:
    no_project = McpConfigTarget(
        global_path=json_mcp_target.global_path,
        project_relative_path=None,
        config_format=json_mcp_target.format,
    )
    assert no_project.install(Scope.PROJECT, tmp_path) is None


def test_uninstall_json_removes_entry(
    tmp_path: Path, json_mcp_target: McpConfigTarget
) -> None:
    json_mcp_target.install(Scope.PROJECT, tmp_path)
    path = json_mcp_target.path_for(Scope.PROJECT, tmp_path)
    assert path is not None
    assert json_mcp_target.uninstall(Scope.PROJECT, tmp_path)
    assert not path.exists()


def test_uninstall_json_keeps_other_servers(
    tmp_path: Path, json_mcp_target: McpConfigTarget
) -> None:
    path = json_mcp_target.path_for(Scope.PROJECT, tmp_path)
    assert path is not None
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(
            {
                "mcpServers": {
                    "other": {"command": "other"},
                    "helix": {"command": "helix", "args": ["serve"]},
                }
            }
        )
    )
    assert json_mcp_target.uninstall(Scope.PROJECT, tmp_path)
    data = json.loads(path.read_text())
    assert "other" in data["mcpServers"]
    assert "helix" not in data["mcpServers"]


def test_uninstall_returns_false_when_not_present(
    tmp_path: Path, json_mcp_target: McpConfigTarget
) -> None:
    assert not json_mcp_target.uninstall(Scope.PROJECT, tmp_path)


def test_uninstall_returns_false_for_empty_file(
    tmp_path: Path, json_mcp_target: McpConfigTarget
) -> None:
    path = json_mcp_target.path_for(Scope.PROJECT, tmp_path)
    assert path is not None
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("")
    assert not json_mcp_target.uninstall(Scope.PROJECT, tmp_path)


def test_uninstall_returns_false_when_helix_absent(
    tmp_path: Path, json_mcp_target: McpConfigTarget
) -> None:
    path = json_mcp_target.path_for(Scope.PROJECT, tmp_path)
    assert path is not None
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps({"mcpServers": {"other": {"command": "other"}}}))
    assert not json_mcp_target.uninstall(Scope.PROJECT, tmp_path)


def test_uninstall_returns_false_for_missing_scope(
    tmp_path: Path, json_mcp_target: McpConfigTarget
) -> None:
    no_project = McpConfigTarget(
        global_path=json_mcp_target.global_path,
        project_relative_path=None,
        config_format=json_mcp_target.format,
    )
    assert not no_project.uninstall(Scope.PROJECT, tmp_path)


# --- Malformed existing config raises from merge/remove (so the shared
# install/uninstall in TextInstallTarget can catch it and log, instead of a
# bare traceback reaching the CLI).


def test_install_json_swallows_invalid_existing_file(
    tmp_path: Path, json_mcp_target: McpConfigTarget
) -> None:
    path = json_mcp_target.path_for(Scope.PROJECT, tmp_path)
    assert path is not None
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("{not valid json")
    assert json_mcp_target.install(Scope.PROJECT, tmp_path) is None
    assert path.read_text() == "{not valid json"


def test_uninstall_json_swallows_invalid_existing_file(
    tmp_path: Path, json_mcp_target: McpConfigTarget
) -> None:
    path = json_mcp_target.path_for(Scope.PROJECT, tmp_path)
    assert path is not None
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("{not valid json")
    assert not json_mcp_target.uninstall(Scope.PROJECT, tmp_path)


def test_merge_raises_invalid_config_error_directly(json_mcp_target: McpConfigTarget) -> None:
    with pytest.raises(InvalidConfigError, match="not valid JSON"):
        json_mcp_target.merge("{not valid json", Path("mcp.json"))


# --- TOML format ---


def test_install_toml_creates_file(tmp_path: Path, toml_mcp_target: McpConfigTarget) -> None:
    path = toml_mcp_target.install(Scope.GLOBAL, tmp_path)
    assert path is not None and path.exists()
    text = path.read_text()
    assert "[mcp_servers.helix]" in text
    assert 'command = "helix"' in text
    assert 'args = ["serve"]' in text


def test_install_toml_appends_to_existing(
    tmp_path: Path, toml_mcp_target: McpConfigTarget
) -> None:
    path = toml_mcp_target.path_for(Scope.GLOBAL, tmp_path)
    assert path is not None
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text('[other_section]\nkey = "value"\n')

    toml_mcp_target.install(Scope.GLOBAL, tmp_path)
    text = path.read_text()
    assert "[other_section]" in text
    assert "[mcp_servers.helix]" in text


def test_install_toml_is_idempotent(
    tmp_path: Path, toml_mcp_target: McpConfigTarget
) -> None:
    toml_mcp_target.install(Scope.GLOBAL, tmp_path)
    toml_mcp_target.install(Scope.GLOBAL, tmp_path)
    path = toml_mcp_target.path_for(Scope.GLOBAL, tmp_path)
    assert path is not None
    assert path.read_text().count("[mcp_servers.helix]") == 1


def test_uninstall_toml_removes_section(
    tmp_path: Path, toml_mcp_target: McpConfigTarget
) -> None:
    toml_mcp_target.install(Scope.GLOBAL, tmp_path)
    path = toml_mcp_target.path_for(Scope.GLOBAL, tmp_path)
    assert path is not None
    assert toml_mcp_target.uninstall(Scope.GLOBAL, tmp_path)
    assert not path.exists()


def test_uninstall_toml_keeps_other_content(
    tmp_path: Path, toml_mcp_target: McpConfigTarget
) -> None:
    path = toml_mcp_target.path_for(Scope.GLOBAL, tmp_path)
    assert path is not None
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        '[other_section]\nkey = "value"\n\n'
        '[mcp_servers.helix]\ncommand = "helix"\nargs = ["serve"]\n'
    )
    assert toml_mcp_target.uninstall(Scope.GLOBAL, tmp_path)
    text = path.read_text()
    assert "[other_section]" in text
    assert "[mcp_servers.helix]" not in text


def test_uninstall_toml_returns_false_when_helix_absent(
    tmp_path: Path, toml_mcp_target: McpConfigTarget
) -> None:
    path = toml_mcp_target.path_for(Scope.GLOBAL, tmp_path)
    assert path is not None
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text('[other_section]\nkey = "value"\n')
    assert not toml_mcp_target.uninstall(Scope.GLOBAL, tmp_path)


def test_install_toml_wraps_block_in_markers(
    tmp_path: Path, toml_mcp_target: McpConfigTarget
) -> None:
    path = toml_mcp_target.install(Scope.GLOBAL, tmp_path)
    assert path is not None
    text = path.read_text()
    assert TOML_START in text
    assert TOML_END in text


def test_uninstall_toml_removes_marked_block_despite_manual_edit(
    tmp_path: Path, toml_mcp_target: McpConfigTarget
) -> None:
    path = toml_mcp_target.path_for(Scope.GLOBAL, tmp_path)
    assert path is not None
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        '[other_section]\nkey = "value"\n\n'
        f"{TOML_START}\n"
        '[mcp_servers.helix]\ncommand = "helix"\nargs = ["serve"]\n'
        'env = { FOO = "bar" }\n'
        f"{TOML_END}\n"
    )
    assert toml_mcp_target.uninstall(Scope.GLOBAL, tmp_path)
    text = path.read_text()
    assert "[other_section]" in text
    assert "[mcp_servers.helix]" not in text
    assert "FOO" not in text


def test_install_toml_does_not_duplicate_legacy_unmarked_header(
    tmp_path: Path, toml_mcp_target: McpConfigTarget
) -> None:
    path = toml_mcp_target.path_for(Scope.GLOBAL, tmp_path)
    assert path is not None
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text('[mcp_servers.helix]\ncommand = "helix"\nargs = ["serve"]\n')

    toml_mcp_target.install(Scope.GLOBAL, tmp_path)
    text = path.read_text()
    assert text.count("[mcp_servers.helix]") == 1
    assert TOML_START not in text


def test_reinstall_toml_replaces_marked_block_in_place(
    tmp_path: Path, toml_mcp_target: McpConfigTarget
) -> None:
    toml_mcp_target.install(Scope.GLOBAL, tmp_path)
    toml_mcp_target.install(Scope.GLOBAL, tmp_path)
    path = toml_mcp_target.path_for(Scope.GLOBAL, tmp_path)
    assert path is not None
    text = path.read_text()
    assert text.count(TOML_START) == 1
    assert text.count("[mcp_servers.helix]") == 1


# --- OpenCode format: `mcp.<name>` with a `local`/`command`-array shape,
# not the generic `mcpServers` object OpenCode's schema doesn't recognize.


def test_install_opencode_creates_file(
    tmp_path: Path, opencode_mcp_target: McpConfigTarget
) -> None:
    path = opencode_mcp_target.install(Scope.PROJECT, tmp_path)
    assert path is not None and path.exists()
    data = json.loads(path.read_text())
    assert data["mcp"]["helix"] == {
        "type": "local",
        "command": ["helix", "serve"],
        "enabled": True,
    }


def test_install_opencode_merges_into_existing(
    tmp_path: Path, opencode_mcp_target: McpConfigTarget
) -> None:
    path = opencode_mcp_target.path_for(Scope.PROJECT, tmp_path)
    assert path is not None
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps({"mcp": {"other": {"type": "local", "command": ["other"]}}}))

    opencode_mcp_target.install(Scope.PROJECT, tmp_path)
    data = json.loads(path.read_text())
    assert "other" in data["mcp"]
    assert data["mcp"]["helix"]["command"] == ["helix", "serve"]


def test_install_opencode_is_idempotent(
    tmp_path: Path, opencode_mcp_target: McpConfigTarget
) -> None:
    opencode_mcp_target.install(Scope.PROJECT, tmp_path)
    opencode_mcp_target.install(Scope.PROJECT, tmp_path)
    path = opencode_mcp_target.path_for(Scope.PROJECT, tmp_path)
    assert path is not None
    data = json.loads(path.read_text())
    assert list(data["mcp"].keys()).count("helix") == 1


def test_uninstall_opencode_removes_entry(
    tmp_path: Path, opencode_mcp_target: McpConfigTarget
) -> None:
    opencode_mcp_target.install(Scope.PROJECT, tmp_path)
    assert opencode_mcp_target.uninstall(Scope.PROJECT, tmp_path)
    path = opencode_mcp_target.path_for(Scope.PROJECT, tmp_path)
    assert path is not None
    assert not path.exists()


def test_uninstall_opencode_keeps_other_servers(
    tmp_path: Path, opencode_mcp_target: McpConfigTarget
) -> None:
    path = opencode_mcp_target.path_for(Scope.PROJECT, tmp_path)
    assert path is not None
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(
            {
                "mcp": {
                    "other": {"type": "local", "command": ["other"]},
                    "helix": {
                        "type": "local",
                        "command": ["helix", "serve"],
                        "enabled": True,
                    },
                }
            }
        )
    )
    assert opencode_mcp_target.uninstall(Scope.PROJECT, tmp_path)
    data = json.loads(path.read_text())
    assert "other" in data["mcp"]
    assert "helix" not in data["mcp"]
