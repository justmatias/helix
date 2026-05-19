from collections.abc import Callable, Iterator
from pathlib import Path
from typing import Any

import pytest
import typer

from helix.core import Brain, Client, Scope, clients, install


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
def working_dir(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> Path:
    """The directory CLI commands operate in (project root)."""
    monkeypatch.chdir(tmp_path)
    return tmp_path


@pytest.fixture
def claude() -> Client:
    """The Claude Code client definition."""
    return next(client for client in clients() if client.key == "claude")


@pytest.fixture
def _install_claude_client(claude: Client, working_dir: Path) -> None:
    """Install a helix block for the Claude Code client in ``working_dir``."""
    install(claude, Scope.PROJECT, working_dir)
