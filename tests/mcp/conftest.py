from collections.abc import Callable

import pytest

from helix.core import Brain


@pytest.fixture(autouse=True)
def _initialize_brain(brain: Brain) -> None:
    brain.initialize()


@pytest.fixture
def convention_names() -> Callable[[list[str]], list[str]]:
    """Extract bare convention names from Brain index lines."""
    return lambda lines: [line.split("[")[1].split("]")[0] for line in lines]
