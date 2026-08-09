from collections.abc import Callable, Iterator
from pathlib import Path
from typing import Any

import pytest
import typer

from helix.core import Brain, Client, Scope, Settings, clients


@pytest.fixture
def set_answers(
    monkeypatch: pytest.MonkeyPatch,
) -> Callable[..., None]:
    """Return a callable that feeds ``typer.prompt`` a fixed answer sequence."""

    def _set(*values: Any) -> None:
        it: Iterator[Any] = iter(values)
        monkeypatch.setattr(typer, "prompt", lambda *a, **k: next(it))

    return _set


@pytest.fixture(autouse=True)
def _initialize_brain(brain: Brain) -> None:
    brain.initialize()


@pytest.fixture
def _remember_convention() -> None:
    """Seed a single ``conv-a`` convention tagged ``python``."""
    Brain().remember(name="conv-a", body="Body A.", tags=["python"])


@pytest.fixture
def _chdir_to_tmp_path(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    """Change into ``tmp_path``, so CLI commands operate on a scratch project root."""
    monkeypatch.chdir(tmp_path)


@pytest.fixture
def working_dir(_chdir_to_tmp_path: None, tmp_path: Path) -> Path:
    """The directory CLI commands operate in (project root)."""
    return tmp_path


@pytest.fixture
def claude() -> Client:
    """The Claude Code client definition."""
    return next(client for client in clients() if client.key == "claude")


@pytest.fixture
def _create_claude_directory() -> None:
    """Make Claude Code look installed, so client detection finds exactly one."""
    (Settings.HOME_DIRECTORY / ".claude").mkdir(parents=True, exist_ok=True)


@pytest.fixture
def _install_claude_client(claude: Client, working_dir: Path) -> None:
    """Install the helix snippet block for the Claude Code client in ``working_dir``."""
    claude.snippet.install(Scope.PROJECT, working_dir)
