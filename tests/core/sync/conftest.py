import subprocess
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
def _remember_convention(brain: Brain) -> None:
    brain.initialize()
    brain.remember(name="conv-a", body="Body A.", tags=["python"])
