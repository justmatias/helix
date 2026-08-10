import pytest

from helix.utils import parse_csv, slugify


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


@pytest.mark.parametrize(
    ("value", "expected"),
    [
        ("Prefer Pydantic v2", "prefer-pydantic-v2"),
        ("Use  *async* I/O!", "use-async-i-o"),
        ("one two three four five six seven", "one-two-three-four-five-six"),
        ("  ", ""),
        ("!!!", ""),
    ],
)
def test_slugify(value: str, expected: str) -> None:
    assert slugify(value) == expected


def test_slugify_respects_max_words() -> None:
    assert slugify("one two three", max_words=2) == "one-two"
