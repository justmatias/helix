from collections.abc import Callable, Generator

import pytest

from helix.core import Brain
from helix.core.settings import Settings


@pytest.fixture
def _require_confirm() -> Generator[None]:
    original = Settings.HELIX_REQUIRE_CONFIRM
    Settings.HELIX_REQUIRE_CONFIRM = True
    yield
    Settings.HELIX_REQUIRE_CONFIRM = original


@pytest.fixture(autouse=True)
def _initialize_brain(brain: Brain) -> None:
    brain.initialize()


@pytest.fixture
def convention_names() -> Callable[[list[str]], list[str]]:
    """Extract bare convention names from Brain index lines."""
    return lambda lines: [line.split("[")[1].split("]")[0] for line in lines]
