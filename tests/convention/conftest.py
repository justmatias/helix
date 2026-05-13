import pytest

from helix.convention import Convention


@pytest.fixture
def sample_convention() -> Convention:
    return Convention(
        name="pydantic-validation",
        body="Prefer Pydantic v2 for boundary validation.",
        tags=["python", "validation"],
        applies_to=["python"],
    )


@pytest.fixture
def minimal_convention() -> Convention:
    return Convention(name="bare", body="Just a body.")
