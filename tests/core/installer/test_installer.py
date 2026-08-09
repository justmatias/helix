import json
import subprocess
from collections.abc import Callable
from pathlib import Path

import pytest

from helix.core import (
    END_MARKER,
    SNIPPET,
    START_MARKER,
    Client,
    InvalidConfigError,
    McpConfigFormat,
    Scope,
    clients,
    detect_installed_clients,
    detect_snippet_blocks,
    install,
    install_hook,
    install_mcp_config,
    uninstall,
    uninstall_mcp_config,
)
from helix.core.installer.hooks import HOOK_COMMAND
from helix.core.installer.mcp_config import (
    CLAUDE_ADD_USER_SCOPE,
    CLAUDE_REMOVE_USER_SCOPE,
    TOML_END,
    TOML_START,
)


def test_install_creates_file_with_block(
    tmp_path: Path, claude_client: Client, claude_md: Path
) -> None:
    path = install(claude_client, Scope.PROJECT, tmp_path)
    text = path.read_text()
    assert path == claude_md
    assert START_MARKER in text
    assert END_MARKER in text
    assert SNIPPET.strip() in text


@pytest.mark.usefixtures("_write_existing_claude_md")
def test_install_appends_to_existing_file(
    tmp_path: Path, claude_client: Client, claude_md: Path, existing_content: str
) -> None:
    install(claude_client, Scope.PROJECT, tmp_path)
    text = claude_md.read_text()
    assert existing_content in text
    assert text.count(START_MARKER) == 1


def test_install_is_idempotent(
    tmp_path: Path, claude_client: Client, claude_md: Path
) -> None:
    install(claude_client, Scope.PROJECT, tmp_path)
    install(claude_client, Scope.PROJECT, tmp_path)
    text = claude_md.read_text()
    assert text.count(START_MARKER) == 1
    assert text.count(END_MARKER) == 1


def test_install_global_uses_settings_home(
    tmp_path: Path, claude_client: Client, global_claude_md: Path
) -> None:
    path = install(claude_client, Scope.GLOBAL, tmp_path)
    assert path == global_claude_md
    assert path.exists()


@pytest.mark.usefixtures("_write_existing_claude_md")
def test_uninstall_removes_block_keeping_other_content(
    tmp_path: Path, claude_client: Client, claude_md: Path, existing_content: str
) -> None:
    install(claude_client, Scope.PROJECT, tmp_path)
    assert uninstall(claude_client, Scope.PROJECT, tmp_path)

    text = claude_md.read_text()
    assert START_MARKER not in text
    assert existing_content in text


def test_uninstall_deletes_file_when_only_block(
    tmp_path: Path, claude_client: Client, claude_md: Path
) -> None:
    install(claude_client, Scope.PROJECT, tmp_path)
    assert uninstall(claude_client, Scope.PROJECT, tmp_path)
    assert not claude_md.exists()


def test_uninstall_returns_false_when_missing(
    tmp_path: Path, claude_client: Client
) -> None:
    assert not uninstall(claude_client, Scope.PROJECT, tmp_path)


@pytest.mark.usefixtures("_write_existing_claude_md")
def test_uninstall_returns_false_when_no_block_in_existing_file(
    tmp_path: Path, claude_client: Client, claude_md: Path, existing_content: str
) -> None:
    assert not uninstall(claude_client, Scope.PROJECT, tmp_path)
    assert claude_md.read_text() == existing_content


@pytest.mark.usefixtures("_create_claude_global_directory")
def test_detect_installed_clients_finds_claude() -> None:
    detected = {client.key for client in detect_installed_clients()}
    assert "claude" in detected
    assert "cursor" not in detected


@pytest.mark.usefixtures("_create_cursor_global_directory")
def test_detect_installed_clients_finds_cursor_via_dot_cursor_dir() -> None:
    detected = {client.key for client in detect_installed_clients()}
    assert "cursor" in detected


def test_clients_include_codex_and_opencode() -> None:
    keys = {client.key for client in clients()}
    assert {"claude", "cursor", "codex", "opencode"} == keys


def test_cursor_install_includes_frontmatter(
    tmp_path: Path, cursor_client: Client
) -> None:
    path = install(cursor_client, Scope.PROJECT, tmp_path)
    text = path.read_text()
    assert text.startswith("---\nalwaysApply: true\n---")
    assert START_MARKER in text


def test_cursor_install_preserves_existing_frontmatter(
    tmp_path: Path, cursor_client: Client
) -> None:
    mdc_path = cursor_client.path_for(Scope.PROJECT, tmp_path)
    mdc_path.parent.mkdir(parents=True, exist_ok=True)
    existing = "---\nalwaysApply: true\n---\n\nSome existing content.\n"
    mdc_path.write_text(existing)

    install(cursor_client, Scope.PROJECT, tmp_path)
    text = mdc_path.read_text()
    assert text.count("---\nalwaysApply: true\n---") == 1
    assert "Some existing content." in text
    assert START_MARKER in text


def test_detect_snippet_blocks_lists_written_locations(
    tmp_path: Path, claude_client: Client
) -> None:
    install(claude_client, Scope.PROJECT, tmp_path)
    install(claude_client, Scope.GLOBAL, tmp_path)
    blocks = detect_snippet_blocks(tmp_path)
    scopes = {block.scope for block in blocks}
    assert scopes == {Scope.PROJECT, Scope.GLOBAL}


@pytest.mark.usefixtures("_write_existing_claude_md")
def test_detect_snippet_blocks_skips_files_without_marker(tmp_path: Path) -> None:
    assert not detect_snippet_blocks(tmp_path)


def test_install_mcp_config_json_creates_file(
    tmp_path: Path, json_mcp_client: Client
) -> None:
    path = install_mcp_config(json_mcp_client, Scope.PROJECT, tmp_path)
    assert path is not None and path.exists()
    data = json.loads(path.read_text())
    assert data["mcpServers"]["helix"] == {"command": "helix", "args": ["serve"]}


def test_install_mcp_config_json_merges_into_existing(
    tmp_path: Path, json_mcp_client: Client, json_mcp_project_path: Path
) -> None:
    json_mcp_project_path.write_text(
        json.dumps({"mcpServers": {"other": {"command": "other"}}})
    )

    install_mcp_config(json_mcp_client, Scope.PROJECT, tmp_path)
    data = json.loads(json_mcp_project_path.read_text())
    assert "other" in data["mcpServers"]
    assert data["mcpServers"]["helix"] == {"command": "helix", "args": ["serve"]}


def test_install_mcp_config_json_is_idempotent(
    tmp_path: Path, json_mcp_client: Client, json_mcp_project_path: Path
) -> None:
    install_mcp_config(json_mcp_client, Scope.PROJECT, tmp_path)
    install_mcp_config(json_mcp_client, Scope.PROJECT, tmp_path)
    data = json.loads(json_mcp_project_path.read_text())
    assert list(data["mcpServers"].keys()).count("helix") == 1


def test_install_mcp_config_returns_none_for_missing_scope(
    tmp_path: Path, json_mcp_client: Client
) -> None:
    no_project_client = json_mcp_client.model_copy(
        update={"mcp_project_relative_path": None}
    )
    result = install_mcp_config(no_project_client, Scope.PROJECT, tmp_path)
    assert result is None


def test_uninstall_mcp_config_json_removes_entry(
    tmp_path: Path, json_mcp_client: Client, json_mcp_project_path: Path
) -> None:
    install_mcp_config(json_mcp_client, Scope.PROJECT, tmp_path)
    assert uninstall_mcp_config(json_mcp_client, Scope.PROJECT, tmp_path)
    assert not json_mcp_project_path.exists()


def test_uninstall_mcp_config_json_keeps_other_servers(
    tmp_path: Path, json_mcp_client: Client, json_mcp_project_path: Path
) -> None:
    json_mcp_project_path.write_text(
        json.dumps({
            "mcpServers": {
                "other": {"command": "other"},
                "helix": {"command": "helix", "args": ["serve"]},
            }
        })
    )
    assert uninstall_mcp_config(json_mcp_client, Scope.PROJECT, tmp_path)
    data = json.loads(json_mcp_project_path.read_text())
    assert "other" in data["mcpServers"]
    assert "helix" not in data["mcpServers"]


def test_uninstall_mcp_config_returns_false_when_not_present(
    tmp_path: Path, json_mcp_client: Client
) -> None:
    assert not uninstall_mcp_config(json_mcp_client, Scope.PROJECT, tmp_path)


def test_uninstall_mcp_config_json_returns_false_for_empty_file(
    tmp_path: Path, json_mcp_client: Client, json_mcp_project_path: Path
) -> None:
    json_mcp_project_path.write_text("")
    assert not uninstall_mcp_config(json_mcp_client, Scope.PROJECT, tmp_path)


def test_uninstall_mcp_config_json_returns_false_when_helix_absent(
    tmp_path: Path, json_mcp_client: Client, json_mcp_project_path: Path
) -> None:
    json_mcp_project_path.write_text(
        json.dumps({"mcpServers": {"other": {"command": "other"}}})
    )
    assert not uninstall_mcp_config(json_mcp_client, Scope.PROJECT, tmp_path)


def test_uninstall_mcp_config_toml_returns_false_when_helix_absent(
    tmp_path: Path, toml_mcp_client: Client, toml_mcp_global_path: Path
) -> None:
    toml_mcp_global_path.write_text('[other_section]\nkey = "value"\n')
    assert not uninstall_mcp_config(toml_mcp_client, Scope.GLOBAL, tmp_path)


def test_install_mcp_config_toml_creates_file(
    tmp_path: Path, toml_mcp_client: Client
) -> None:
    path = install_mcp_config(toml_mcp_client, Scope.GLOBAL, tmp_path)
    assert path is not None and path.exists()
    text = path.read_text()
    assert "[mcp_servers.helix]" in text
    assert 'command = "helix"' in text
    assert 'args = ["serve"]' in text


def test_install_mcp_config_toml_appends_to_existing(
    tmp_path: Path, toml_mcp_client: Client, toml_mcp_global_path: Path
) -> None:
    toml_mcp_global_path.write_text('[other_section]\nkey = "value"\n')

    install_mcp_config(toml_mcp_client, Scope.GLOBAL, tmp_path)
    text = toml_mcp_global_path.read_text()
    assert "[other_section]" in text
    assert "[mcp_servers.helix]" in text


def test_install_mcp_config_toml_is_idempotent(
    tmp_path: Path, toml_mcp_client: Client, toml_mcp_global_path: Path
) -> None:
    install_mcp_config(toml_mcp_client, Scope.GLOBAL, tmp_path)
    install_mcp_config(toml_mcp_client, Scope.GLOBAL, tmp_path)
    assert toml_mcp_global_path.read_text().count("[mcp_servers.helix]") == 1


def test_uninstall_mcp_config_toml_removes_section(
    tmp_path: Path, toml_mcp_client: Client, toml_mcp_global_path: Path
) -> None:
    install_mcp_config(toml_mcp_client, Scope.GLOBAL, tmp_path)
    assert uninstall_mcp_config(toml_mcp_client, Scope.GLOBAL, tmp_path)
    assert not toml_mcp_global_path.exists()


def test_uninstall_mcp_config_toml_keeps_other_content(
    tmp_path: Path, toml_mcp_client: Client, toml_mcp_global_path: Path
) -> None:
    toml_mcp_global_path.write_text(
        '[other_section]\nkey = "value"\n\n'
        '[mcp_servers.helix]\ncommand = "helix"\nargs = ["serve"]\n'
    )
    assert uninstall_mcp_config(toml_mcp_client, Scope.GLOBAL, tmp_path)
    text = toml_mcp_global_path.read_text()
    assert "[other_section]" in text
    assert "[mcp_servers.helix]" not in text


def test_claude_client_has_json_mcp_config() -> None:
    claude = next(c for c in clients() if c.key == "claude")
    assert claude.mcp_global_path is not None
    assert claude.mcp_global_path.name == ".claude.json"
    assert claude.mcp_project_relative_path == Path(".mcp.json")
    assert claude.mcp_format == McpConfigFormat.JSON


def test_cursor_client_has_json_mcp_config() -> None:
    cursor = next(c for c in clients() if c.key == "cursor")
    assert cursor.mcp_global_path is not None
    assert cursor.mcp_global_path.name == "mcp.json"
    assert cursor.mcp_project_relative_path == Path(".cursor") / "mcp.json"
    assert cursor.mcp_format == McpConfigFormat.JSON


def test_codex_client_has_toml_mcp_config() -> None:
    codex = next(c for c in clients() if c.key == "codex")
    assert codex.mcp_global_path is not None
    assert codex.mcp_global_path.name == "config.toml"
    assert codex.mcp_project_relative_path is None
    assert codex.mcp_format == McpConfigFormat.TOML


def test_opencode_client_has_opencode_mcp_format() -> None:
    opencode = next(c for c in clients() if c.key == "opencode")
    assert opencode.mcp_format == McpConfigFormat.OPENCODE


# --- opencode MCP format: `mcp.<name>` with a `local`/`command`-array shape,
# not the generic `mcpServers` object opencode's schema doesn't recognize.


def test_install_mcp_config_opencode_creates_file(
    tmp_path: Path, opencode_mcp_client: Client
) -> None:
    path = install_mcp_config(opencode_mcp_client, Scope.PROJECT, tmp_path)
    assert path is not None and path.exists()
    data = json.loads(path.read_text())
    assert data["mcp"]["helix"] == {
        "type": "local",
        "command": ["helix", "serve"],
        "enabled": True,
    }


def test_install_mcp_config_opencode_merges_into_existing(
    tmp_path: Path, opencode_mcp_client: Client, opencode_mcp_project_path: Path
) -> None:
    opencode_mcp_project_path.write_text(
        json.dumps({"mcp": {"other": {"type": "local", "command": ["other"]}}})
    )
    install_mcp_config(opencode_mcp_client, Scope.PROJECT, tmp_path)
    data = json.loads(opencode_mcp_project_path.read_text())
    assert "other" in data["mcp"]
    assert data["mcp"]["helix"]["command"] == ["helix", "serve"]


def test_install_mcp_config_opencode_is_idempotent(
    tmp_path: Path, opencode_mcp_client: Client, opencode_mcp_project_path: Path
) -> None:
    install_mcp_config(opencode_mcp_client, Scope.PROJECT, tmp_path)
    install_mcp_config(opencode_mcp_client, Scope.PROJECT, tmp_path)
    data = json.loads(opencode_mcp_project_path.read_text())
    assert list(data["mcp"].keys()).count("helix") == 1


def test_uninstall_mcp_config_opencode_removes_entry(
    tmp_path: Path, opencode_mcp_client: Client, opencode_mcp_project_path: Path
) -> None:
    install_mcp_config(opencode_mcp_client, Scope.PROJECT, tmp_path)
    assert uninstall_mcp_config(opencode_mcp_client, Scope.PROJECT, tmp_path)
    assert not opencode_mcp_project_path.exists()


def test_uninstall_mcp_config_opencode_keeps_other_servers(
    tmp_path: Path, opencode_mcp_client: Client, opencode_mcp_project_path: Path
) -> None:
    opencode_mcp_project_path.write_text(
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
    assert uninstall_mcp_config(opencode_mcp_client, Scope.PROJECT, tmp_path)
    data = json.loads(opencode_mcp_project_path.read_text())
    assert "other" in data["mcp"]
    assert "helix" not in data["mcp"]


# --- TOML block is now marker-wrapped, so uninstall survives hand-edits
# (like an added `env` line) inside the block, unlike an exact-string match.


def test_install_mcp_config_toml_wraps_block_in_markers(
    tmp_path: Path, toml_mcp_client: Client
) -> None:
    path = install_mcp_config(toml_mcp_client, Scope.GLOBAL, tmp_path)
    assert path is not None
    text = path.read_text()
    assert TOML_START in text
    assert TOML_END in text


def test_uninstall_mcp_config_toml_removes_marked_block_despite_manual_edit(
    tmp_path: Path, toml_mcp_client: Client, toml_mcp_global_path: Path
) -> None:
    toml_mcp_global_path.write_text(
        '[other_section]\nkey = "value"\n\n'
        f"{TOML_START}\n"
        '[mcp_servers.helix]\ncommand = "helix"\nargs = ["serve"]\n'
        'env = { FOO = "bar" }\n'
        f"{TOML_END}\n"
    )
    assert uninstall_mcp_config(toml_mcp_client, Scope.GLOBAL, tmp_path)
    text = toml_mcp_global_path.read_text()
    assert "[other_section]" in text
    assert "[mcp_servers.helix]" not in text
    assert "FOO" not in text


def test_install_mcp_config_toml_does_not_duplicate_legacy_unmarked_header(
    tmp_path: Path, toml_mcp_client: Client, toml_mcp_global_path: Path
) -> None:
    toml_mcp_global_path.write_text(
        '[mcp_servers.helix]\ncommand = "helix"\nargs = ["serve"]\n'
    )
    install_mcp_config(toml_mcp_client, Scope.GLOBAL, tmp_path)
    text = toml_mcp_global_path.read_text()
    assert text.count("[mcp_servers.helix]") == 1
    assert TOML_START not in text


def test_uninstall_mcp_config_returns_false_for_missing_scope(
    tmp_path: Path, json_mcp_client: Client
) -> None:
    no_project_client = json_mcp_client.model_copy(
        update={"mcp_project_relative_path": None}
    )
    assert not uninstall_mcp_config(no_project_client, Scope.PROJECT, tmp_path)


def test_reinstall_toml_replaces_marked_block_in_place(
    tmp_path: Path, toml_mcp_client: Client, toml_mcp_global_path: Path
) -> None:
    install_mcp_config(toml_mcp_client, Scope.GLOBAL, tmp_path)
    install_mcp_config(toml_mcp_client, Scope.GLOBAL, tmp_path)
    text = toml_mcp_global_path.read_text()
    assert text.count(TOML_START) == 1
    assert text.count("[mcp_servers.helix]") == 1


# --- Malformed existing config files raise instead of crashing with a
# bare traceback, so the CLI can report which client/file needs attention.


def test_install_mcp_config_json_raises_on_invalid_existing_file(
    tmp_path: Path, json_mcp_client: Client, json_mcp_project_path: Path
) -> None:
    json_mcp_project_path.write_text("{not valid json")
    with pytest.raises(InvalidConfigError, match="not valid JSON"):
        install_mcp_config(json_mcp_client, Scope.PROJECT, tmp_path)


def test_uninstall_mcp_config_json_raises_on_invalid_existing_file(
    tmp_path: Path, json_mcp_client: Client, json_mcp_project_path: Path
) -> None:
    json_mcp_project_path.write_text("{not valid json")
    with pytest.raises(InvalidConfigError, match="not valid JSON"):
        uninstall_mcp_config(json_mcp_client, Scope.PROJECT, tmp_path)


def test_install_hook_raises_on_invalid_existing_settings(
    tmp_path: Path, hook_client: Client, hook_global_path: Path
) -> None:
    hook_global_path.write_text("{not valid json")
    with pytest.raises(InvalidConfigError, match="not valid JSON"):
        install_hook(hook_client, Scope.GLOBAL, tmp_path)


# --- Claude Code's global MCP scope lives in ~/.claude.json, which also
# holds live session state. When the `claude` CLI is on PATH, delegate to it
# instead of rewriting that file directly.


def _recording_run(
    calls: list[list[str]],
) -> Callable[..., subprocess.CompletedProcess]:
    def _run(cmd: list[str], **_kwargs: object) -> subprocess.CompletedProcess:
        calls.append(cmd)
        return subprocess.CompletedProcess(cmd, 0)

    return _run


def test_install_mcp_config_claude_global_uses_cli_when_available(
    tmp_path: Path, claude_client: Client, monkeypatch: pytest.MonkeyPatch
) -> None:
    calls: list[list[str]] = []
    monkeypatch.setattr(
        "helix.core.installer.mcp_config.shutil.which", lambda _name: "/usr/bin/claude"
    )
    monkeypatch.setattr(
        "helix.core.installer.mcp_config.subprocess.run", _recording_run(calls)
    )

    result = install_mcp_config(claude_client, Scope.GLOBAL, tmp_path)

    assert result == claude_client.mcp_global_path
    assert calls == [CLAUDE_ADD_USER_SCOPE]
    assert claude_client.mcp_global_path is not None
    assert not claude_client.mcp_global_path.exists()


def test_install_mcp_config_claude_global_falls_back_without_cli(
    tmp_path: Path, claude_client: Client, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setattr(
        "helix.core.installer.mcp_config.shutil.which", lambda _name: None
    )
    path = install_mcp_config(claude_client, Scope.GLOBAL, tmp_path)
    assert path is not None and path.exists()
    data = json.loads(path.read_text())
    assert data["mcpServers"]["helix"] == {"command": "helix", "args": ["serve"]}


def test_install_mcp_config_claude_project_scope_never_uses_cli(
    tmp_path: Path, claude_client: Client, monkeypatch: pytest.MonkeyPatch
) -> None:
    calls: list[list[str]] = []
    monkeypatch.setattr(
        "helix.core.installer.mcp_config.shutil.which", lambda _name: "/usr/bin/claude"
    )
    monkeypatch.setattr(
        "helix.core.installer.mcp_config.subprocess.run", _recording_run(calls)
    )
    path = install_mcp_config(claude_client, Scope.PROJECT, tmp_path)
    assert not calls
    assert path is not None and path.exists()


def test_uninstall_mcp_config_claude_global_uses_cli_when_available(
    tmp_path: Path, claude_client: Client, monkeypatch: pytest.MonkeyPatch
) -> None:
    calls: list[list[str]] = []
    monkeypatch.setattr(
        "helix.core.installer.mcp_config.shutil.which", lambda _name: "/usr/bin/claude"
    )
    monkeypatch.setattr(
        "helix.core.installer.mcp_config.subprocess.run", _recording_run(calls)
    )

    assert uninstall_mcp_config(claude_client, Scope.GLOBAL, tmp_path)
    assert calls == [CLAUDE_REMOVE_USER_SCOPE]


def test_uninstall_mcp_config_claude_global_reports_cli_failure(
    tmp_path: Path, claude_client: Client, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setattr(
        "helix.core.installer.mcp_config.shutil.which", lambda _name: "/usr/bin/claude"
    )
    monkeypatch.setattr(
        "helix.core.installer.mcp_config.subprocess.run",
        lambda cmd, **_kwargs: subprocess.CompletedProcess(cmd, 1),
    )
    assert not uninstall_mcp_config(claude_client, Scope.GLOBAL, tmp_path)


# --- Detection now covers orphaned MCP/hook entries even without a
# surviving markdown snippet, so uninstall doesn't leak them.


def test_detect_snippet_blocks_finds_mcp_only_leftover(
    tmp_path: Path,
    json_mcp_client: Client,
    json_mcp_project_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    json_mcp_project_path.write_text(
        json.dumps({"mcpServers": {"helix": {"command": "helix", "args": ["serve"]}}})
    )
    monkeypatch.setattr(
        "helix.core.installer.operations.all_clients", lambda: [json_mcp_client]
    )

    blocks = [
        block for block in detect_snippet_blocks(tmp_path) if block.scope == Scope.PROJECT
    ]
    assert blocks
    assert blocks[0].path == json_mcp_project_path


def test_detect_snippet_blocks_finds_hook_only_leftover(
    tmp_path: Path,
    hook_client: Client,
    hook_global_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    hook_global_path.write_text(
        json.dumps({"hooks": {"SessionStart": [{"hooks": [{"command": HOOK_COMMAND}]}]}})
    )
    monkeypatch.setattr(
        "helix.core.installer.operations.all_clients", lambda: [hook_client]
    )

    blocks = [
        block for block in detect_snippet_blocks(tmp_path) if block.scope == Scope.GLOBAL
    ]
    assert blocks
    assert blocks[0].path == hook_global_path
