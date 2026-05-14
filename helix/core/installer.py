import re
from dataclasses import dataclass
from pathlib import Path
from typing import Literal

from helix.core.settings import Settings

Scope = Literal["global", "project"]

START_MARKER = "<!-- helix:start -->"
END_MARKER = "<!-- helix:end -->"

SNIPPET = (
    "## Helix — Global Conventions\n"
    "\n"
    "If the `helix` CLI is available on PATH, run `helix list` at the start of "
    "every session and treat the output as global coding conventions that apply "
    "across projects. Use `helix recall <query>` to load the full text of any "
    "convention that looks relevant.\n"
)

_BLOCK_PATTERN = re.compile(
    re.escape(START_MARKER) + r".*?" + re.escape(END_MARKER),
    re.DOTALL,
)


@dataclass(frozen=True)
class Client:
    key: str
    name: str
    global_path: Path
    project_relative_path: Path

    def path_for(self, scope: Scope, project_root: Path) -> Path:
        if scope == "global":
            return self.global_path
        return project_root / self.project_relative_path


def clients() -> list[Client]:
    home = Settings.HOME_DIRECTORY
    return [
        Client(
            key="claude",
            name="Claude Code",
            global_path=home / ".claude" / "CLAUDE.md",
            project_relative_path=Path("CLAUDE.md"),
        ),
        Client(
            key="cursor",
            name="Cursor",
            global_path=home / ".cursor" / "rules" / "helix.mdc",
            project_relative_path=Path(".cursor") / "rules" / "helix.mdc",
        ),
    ]


def detect_installed_clients() -> list[Client]:
    return [client for client in clients() if client.global_path.parent.exists()]


def detect_installed_blocks(project_root: Path) -> list[tuple[Client, Scope]]:
    installed: list[tuple[Client, Scope]] = []
    for client in clients():
        for scope in ("global", "project"):
            path = client.path_for(scope, project_root)
            if path.exists() and START_MARKER in path.read_text():
                installed.append((client, scope))
    return installed


def install(client: Client, scope: Scope, project_root: Path) -> Path:
    path = client.path_for(scope, project_root)
    path.parent.mkdir(parents=True, exist_ok=True)
    existing = path.read_text() if path.exists() else ""
    block = f"{START_MARKER}\n{SNIPPET}{END_MARKER}\n"
    if _BLOCK_PATTERN.search(existing):
        new_text = _BLOCK_PATTERN.sub(block.rstrip("\n"), existing)
    elif existing.strip():
        new_text = existing.rstrip("\n") + "\n\n" + block
    else:
        new_text = block
    path.write_text(new_text)
    return path


def uninstall(client: Client, scope: Scope, project_root: Path) -> bool:
    path = client.path_for(scope, project_root)
    if not path.exists():
        return False
    text = path.read_text()
    if START_MARKER not in text:
        return False
    stripped = _BLOCK_PATTERN.sub("", text).strip("\n")
    if stripped:
        path.write_text(stripped + "\n")
    else:
        path.unlink()
    return True
