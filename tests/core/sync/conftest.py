import subprocess
from collections.abc import Callable
from pathlib import Path

import pytest

from helix.core import Brain


@pytest.fixture
def remote_repository(tmp_path: Path) -> str:
    """A bare git repository, usable as a sync remote without any network access."""
    remote = tmp_path / "remote.git"
    subprocess.run(["git", "init", "--bare", "-q", str(remote)], check=True)
    return str(remote)


@pytest.fixture
def remote_files(remote_repository: str) -> Callable[[], list[str]]:
    """Callable returning the convention filenames currently pushed to the remote's main branch."""

    def _remote_files() -> list[str]:
        result = subprocess.run(
            ["git", "ls-tree", "--name-only", "-r", "main", "--", "conventions"],
            cwd=remote_repository,
            check=True,
            capture_output=True,
            text=True,
        )
        return sorted(Path(p).name for p in result.stdout.splitlines())

    return _remote_files


@pytest.fixture
def _remember_convention(brain: Brain) -> None:
    brain.initialize()
    brain.remember(name="conv-a", body="Body A.", tags=["python"])
