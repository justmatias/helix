from collections.abc import Generator
from pathlib import Path

import pytest

from helix.core.brain import Brain
from helix.core.settings import Settings


@pytest.fixture(autouse=True)
def _patch_storage_settings(tmp_path: Path) -> Generator[None]:
    old_value = Settings.HOME_DIRECTORY
    Settings.HOME_DIRECTORY = tmp_path
    yield
    Settings.HOME_DIRECTORY = old_value


@pytest.fixture
def brain() -> Brain:
    return Brain()


@pytest.fixture
def _initialize_brain(brain: Brain) -> None:
    brain.initialize()
