import pytest

from helix.core import Brain


@pytest.fixture
def _initialize_brain(brain: Brain) -> None:
    brain.initialize()
