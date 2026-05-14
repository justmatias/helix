import pytest

from helix.utils import parse_csv


@pytest.mark.parametrize(
    ("value", "expected"),
    [
        (None, []),
        ("", []),
        ("one", ["one"]),
        ("one,two,three", ["one", "two", "three"]),
        (" one , two ,three ", ["one", "two", "three"]),
        ("one,,two", ["one", "", "two"]),
    ],
)
def test_parse_csv(value: str | None, expected: list[str]) -> None:
    assert parse_csv(value) == expected
