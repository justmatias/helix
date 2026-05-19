from pathlib import Path

import pytest

from helix.core import clients
from helix.core.installer.models import Client


@pytest.fixture
def claude_client() -> Client:
    return next(client for client in clients() if client.key == "claude")


@pytest.fixture
def claude_md(tmp_path: Path) -> Path:
    return tmp_path / "CLAUDE.md"


@pytest.fixture
def global_claude_md(tmp_path: Path) -> Path:
    return tmp_path / ".claude" / "CLAUDE.md"


@pytest.fixture
def existing_content() -> str:
    return "# Project Notes\n\nExisting content.\n"


@pytest.fixture
def _write_existing_claude_md(claude_md: Path, existing_content: str) -> None:
    claude_md.write_text(existing_content)


@pytest.fixture
def _create_claude_global_directory(tmp_path: Path) -> None:
    (tmp_path / ".claude").mkdir()
