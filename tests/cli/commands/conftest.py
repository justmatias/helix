import pytest

from helix.core import Brain


@pytest.fixture(autouse=True)
def _initialize_brain(brain: Brain) -> None:
    brain.initialize()
