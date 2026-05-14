import pytest
from typer.testing import CliRunner

from helix.core import Settings


@pytest.fixture(autouse=True)
def _remove_index() -> None:
    Settings.HELIX_INDEX.unlink(missing_ok=True)


@pytest.fixture
def runner() -> CliRunner:
    return CliRunner()
