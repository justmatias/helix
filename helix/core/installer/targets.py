"""Install targets: the artifacts Helix can write into a client's config.

Each target — an instruction snippet, an MCP server entry, a SessionStart
hook — is a small adapter satisfying InstallTarget's uniform install/
uninstall/exists/path_for shape. Callers (the CLI, detection) loop over a
client's targets without branching on which kind of artifact they are.
"""

import json
import re
import shutil
import subprocess
import sys
from abc import ABC, abstractmethod
from collections.abc import Callable
from dataclasses import dataclass
from pathlib import Path

from .errors import InvalidConfigError
from .json_config import read_json
from .scope import Scope

START_MARKER = "<!-- helix:start -->"
END_MARKER = "<!-- helix:end -->"
SNIPPET = (
    "## Helix — Global Conventions\n"
    "\n"
    "Use `recall` (MCP) or `helix recall <query>` (CLI) to load the full text of "
    "any convention that looks relevant, and `remember` to save a new one when I "
    "state a preference that should outlive this project.\n"
    "\n"
    "If the convention index was not already injected at session start, run "
    "`list_conventions` (MCP) or `helix list` to see it.\n"
)
BLOCK_PATTERN = re.compile(
    re.escape(START_MARKER) + r".*?" + re.escape(END_MARKER), re.DOTALL
)

HOOK_EVENT = "SessionStart"
HOOK_COMMAND = "helix list"
HOOK_ENTRY = {
    "matcher": "startup|resume|clear",
    "hooks": [{"type": "command", "command": HOOK_COMMAND}],
}

HELIX_MCP_ENTRY = {"command": "helix", "args": ["serve"]}
OPENCODE_MCP_ENTRY = {"type": "local", "command": ["helix", "serve"], "enabled": True}

# Codex has no comment-block convention of its own, so Helix wraps its TOML
# table in markers (like the snippet block above) rather than matching the
# table's exact text. That way a hand-added `env = ...` line inside the block
# doesn't defeat uninstall — the whole marked span comes out together.
TOML_START = "# helix-mcp:start"
TOML_END = "# helix-mcp:end"
TOML_HEADER = "[mcp_servers.helix]"
TOML_INNER = f'{TOML_HEADER}\ncommand = "helix"\nargs = ["serve"]\n'
TOML_BLOCK = f"{TOML_START}\n{TOML_INNER}{TOML_END}\n"
TOML_BLOCK_PATTERN = re.compile(
    re.escape(TOML_START) + r".*?" + re.escape(TOML_END), re.DOTALL
)

# Claude Code's global MCP scope lives in ~/.claude.json, which also holds
# live session state for a running client. Prefer the CLI's own migration
# logic over rewriting that file directly, when it's available.
CLAUDE_ADD_USER_SCOPE = ["claude", "mcp", "add", "-s", "user", "helix", "--", "helix", "serve"]
CLAUDE_REMOVE_USER_SCOPE = ["claude", "mcp", "remove", "-s", "user", "helix"]


class InstallTarget(ABC):
    """One artifact Helix can write into a client's config.

    ``install``/``uninstall``/``exists``/``path_for`` share one (scope,
    project_root) shape, so callers loop over a client's targets without
    knowing which kind of artifact each one is.
    """

    label: str = "helix entry"
    needs_restart_notice: bool = False

    @abstractmethod
    def path_for(self, scope: Scope, project_root: Path) -> Path | None: ...

    @abstractmethod
    def install(self, scope: Scope, project_root: Path) -> Path | None: ...

    @abstractmethod
    def uninstall(self, scope: Scope, project_root: Path) -> bool: ...

    @abstractmethod
    def exists(self, scope: Scope, project_root: Path) -> bool: ...


class TextInstallTarget(InstallTarget):
    """An InstallTarget whose install/uninstall are pure text transforms over
    one file. Subclasses implement ``merge``/``remove``/``needle``; file I/O
    and ``InvalidConfigError`` handling live here, once, instead of once per
    artifact type.
    """

    def default_text(self) -> str:
        """Starting content when the file doesn't exist yet."""
        return ""

    @abstractmethod
    def needle(self) -> str:
        """Substring marking this target's entry as present, for ``exists``."""

    @abstractmethod
    def merge(self, existing: str, path: Path) -> str: ...

    @abstractmethod
    def remove(self, existing: str, path: Path) -> str | None: ...

    def install(self, scope: Scope, project_root: Path) -> Path | None:
        path = self.path_for(scope, project_root)
        if path is None:
            return None

        existing = path.read_text() if path.exists() else self.default_text()
        try:
            new_text = self.merge(existing, path)
        except InvalidConfigError as exc:
            print(str(exc), file=sys.stderr)
            return None

        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(new_text)
        return path

    def uninstall(self, scope: Scope, project_root: Path) -> bool:
        path = self.path_for(scope, project_root)
        if path is None or not path.exists():
            return False

        try:
            result = self.remove(path.read_text(), path)
        except InvalidConfigError as exc:
            print(str(exc), file=sys.stderr)
            return False

        if result is None:
            return False
        if result:
            path.write_text(result)
        else:
            path.unlink()
        return True

    def exists(self, scope: Scope, project_root: Path) -> bool:
        path = self.path_for(scope, project_root)
        return path is not None and path.exists() and self.needle() in path.read_text()


class SnippetTarget(TextInstallTarget):
    """The instruction-snippet block every client gets (CLAUDE.md, AGENTS.md, ...)."""

    label = "helix block"

    def __init__(
        self,
        global_path: Path,
        project_relative_path: Path,
        preamble: str | None = None,
    ) -> None:
        self.global_path = global_path
        self.project_relative_path = project_relative_path
        self.preamble = preamble

    def path_for(self, scope: Scope, project_root: Path) -> Path:
        if scope == Scope.GLOBAL:
            return self.global_path
        return project_root / self.project_relative_path

    def default_text(self) -> str:
        return self.preamble or ""

    def needle(self) -> str:
        return START_MARKER

    def merge(self, existing: str, path: Path) -> str:
        block = f"{START_MARKER}\n{SNIPPET}{END_MARKER}\n"
        if BLOCK_PATTERN.search(existing):
            return BLOCK_PATTERN.sub(block.rstrip("\n"), existing)
        if existing.strip():
            return existing.rstrip("\n") + "\n\n" + block
        return block

    def remove(self, existing: str, path: Path) -> str | None:
        if START_MARKER not in existing:
            return None
        remaining = BLOCK_PATTERN.sub("", existing).strip("\n")
        return remaining + "\n" if remaining else ""


class HookTarget(TextInstallTarget):
    """The Claude Code SessionStart hook, so the convention index loads
    without the agent asking. Stronger guarantee than the snippet, which is
    just an instruction the agent might not follow.
    """

    label = "SessionStart hook"
    needs_restart_notice = True

    def __init__(
        self,
        global_path: Path | None,
        project_relative_path: Path | None,
    ) -> None:
        self.global_path = global_path
        self.project_relative_path = project_relative_path

    def path_for(self, scope: Scope, project_root: Path) -> Path | None:
        if scope == Scope.GLOBAL:
            return self.global_path
        if self.project_relative_path is None:
            return None
        return project_root / self.project_relative_path

    def needle(self) -> str:
        return HOOK_COMMAND

    @staticmethod
    def _is_helix_entry(entry: dict) -> bool:
        return any(
            hook.get("command") == HOOK_COMMAND for hook in entry.get("hooks", []) or []
        )

    @staticmethod
    def _prune(data: dict) -> dict:
        hooks = data.get("hooks", {})
        if not hooks.get(HOOK_EVENT):
            hooks.pop(HOOK_EVENT, None)
        if not hooks:
            data.pop("hooks", None)
        return data

    def merge(self, existing: str, path: Path) -> str:
        data = read_json(path, existing)
        entries: list[dict] = data.setdefault("hooks", {}).setdefault(HOOK_EVENT, [])
        if not any(self._is_helix_entry(entry) for entry in entries):
            entries.append(HOOK_ENTRY)
        return json.dumps(data, indent=2) + "\n"

    def remove(self, existing: str, path: Path) -> str | None:
        data = read_json(path, existing)
        entries = data.get("hooks", {}).get(HOOK_EVENT, [])
        remaining = [entry for entry in entries if not self._is_helix_entry(entry)]
        if len(remaining) == len(entries):
            return None
        data["hooks"][HOOK_EVENT] = remaining
        data = self._prune(data)
        return json.dumps(data, indent=2) + "\n" if data else ""


@dataclass(frozen=True)
class ConfigFormat:
    """The file-format-specific slice of an MCP config entry: how to spot,
    merge, and remove it. Injected into ``McpConfigTarget`` so JSON, TOML,
    and OpenCode's JSON-with-different-keys stay one target instead of three.
    """

    needle: str
    merge: Callable[[str, Path], str]
    remove: Callable[[str, Path], str | None]


def _json_family_merge(key: str, entry: dict) -> Callable[[str, Path], str]:
    def _merge(existing: str, path: Path) -> str:
        data = read_json(path, existing)
        data.setdefault(key, {})["helix"] = entry
        return json.dumps(data, indent=2) + "\n"

    return _merge


def _json_family_remove(key: str) -> Callable[[str, Path], str | None]:
    def _remove(existing: str, path: Path) -> str | None:
        if not existing.strip():
            return None
        data = read_json(path, existing)
        servers = data.get(key, {})
        if "helix" not in servers:
            return None
        del servers["helix"]
        if not servers:
            del data[key]
        return json.dumps(data, indent=2) + "\n" if data else ""

    return _remove


def _toml_merge(existing: str, path: Path) -> str:
    if TOML_BLOCK_PATTERN.search(existing):
        return TOML_BLOCK_PATTERN.sub(TOML_BLOCK.rstrip("\n"), existing)
    if TOML_HEADER in existing:
        return existing
    if existing.strip():
        return existing.rstrip("\n") + "\n\n" + TOML_BLOCK
    return TOML_BLOCK


def _toml_remove(existing: str, path: Path) -> str | None:
    if TOML_BLOCK_PATTERN.search(existing):
        remaining = TOML_BLOCK_PATTERN.sub("", existing).strip("\n")
        return remaining + "\n" if remaining else ""
    # Legacy (pre-marker) installs wrote the bare table with no wrapper.
    if TOML_INNER not in existing + "\n":
        return None
    remaining = (existing + "\n").replace(TOML_INNER, "").strip("\n")
    return remaining + "\n" if remaining else ""


JSON_MCP_FORMAT = ConfigFormat(
    needle='"helix"',
    merge=_json_family_merge("mcpServers", HELIX_MCP_ENTRY),
    remove=_json_family_remove("mcpServers"),
)
OPENCODE_MCP_FORMAT = ConfigFormat(
    needle='"helix"',
    merge=_json_family_merge("mcp", OPENCODE_MCP_ENTRY),
    remove=_json_family_remove("mcp"),
)
TOML_MCP_FORMAT = ConfigFormat(
    needle=TOML_HEADER,
    merge=_toml_merge,
    remove=_toml_remove,
)


class McpConfigTarget(TextInstallTarget):
    """The Helix MCP server entry in a client's MCP config file."""

    label = "MCP server config"

    def __init__(
        self,
        global_path: Path | None,
        project_relative_path: Path | None,
        config_format: ConfigFormat,
    ) -> None:
        self.global_path = global_path
        self.project_relative_path = project_relative_path
        self.format = config_format

    def path_for(self, scope: Scope, project_root: Path) -> Path | None:
        if scope == Scope.GLOBAL:
            return self.global_path
        if self.project_relative_path is None:
            return None
        return project_root / self.project_relative_path

    def needle(self) -> str:
        return self.format.needle

    def merge(self, existing: str, path: Path) -> str:
        return self.format.merge(existing, path)

    def remove(self, existing: str, path: Path) -> str | None:
        return self.format.remove(existing, path)


class SubprocessInstallTarget(InstallTarget):
    """An MCP config target that shells out to a client's own CLI for one
    (client, scope) pair instead of rewriting a file directly — used for
    Claude Code's global MCP scope, whose file also holds live session
    state a direct rewrite could clobber. Falls back to the wrapped file
    target for every other scope, or when that CLI isn't on PATH.
    """

    label = "MCP server config"

    def __init__(
        self,
        fallback: McpConfigTarget,
        subprocess_scope: Scope,
        add_command: list[str],
        remove_command: list[str],
    ) -> None:
        self.fallback = fallback
        self.subprocess_scope = subprocess_scope
        self.add_command = add_command
        self.remove_command = remove_command

    def _use_subprocess(self, scope: Scope) -> bool:
        return (
            scope == self.subprocess_scope
            and shutil.which(self.add_command[0]) is not None
        )

    def path_for(self, scope: Scope, project_root: Path) -> Path | None:
        return self.fallback.path_for(scope, project_root)

    def install(self, scope: Scope, project_root: Path) -> Path | None:
        if self._use_subprocess(scope):
            subprocess.run(self.add_command, check=False, capture_output=True)
            return self.fallback.path_for(scope, project_root)
        return self.fallback.install(scope, project_root)

    def uninstall(self, scope: Scope, project_root: Path) -> bool:
        if self._use_subprocess(scope):
            completed = subprocess.run(self.remove_command, check=False, capture_output=True)
            return completed.returncode == 0
        return self.fallback.uninstall(scope, project_root)

    def exists(self, scope: Scope, project_root: Path) -> bool:
        return self.fallback.exists(scope, project_root)
