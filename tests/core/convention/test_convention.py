import pytest

from helix.core.convention import Convention


def test_convention_to_markdown_contains_frontmatter(sample_convention: Convention) -> None:
    markdown =sample_convention.to_markdown()
    assert "name: pydantic-validation" in markdown
    assert "python" in markdown
    assert "Prefer Pydantic v2 for boundary validation." in markdown


def test_convention_to_markdown_empty_lists(minimal_convention: Convention) -> None:
    markdown =minimal_convention.to_markdown()
    assert "tags:" in markdown
    assert "applies_to:" in markdown


def test_convention_roundtrip(sample_convention: Convention) -> None:
    restored = Convention.from_markdown(sample_convention.to_markdown())
    assert restored.name == sample_convention.name
    assert restored.body == sample_convention.body
    assert restored.tags == sample_convention.tags
    assert restored.applies_to == sample_convention.applies_to


def test_convention_from_markdown_invalid_no_delimiters() -> None:
    with pytest.raises(ValueError, match="name"):
        Convention.from_markdown("no frontmatter here")


def test_convention_from_markdown_missing_name() -> None:
    with pytest.raises(ValueError, match="name"):
        Convention.from_markdown("---\ntags: [python]\n---\n\nBody.\n")


def test_convention_index_line_format(sample_convention: Convention) -> None:
    line = sample_convention.index_line()
    assert line.startswith("- [pydantic-validation](conventions/pydantic-validation.md)")
    assert "[python,validation]" in line
    assert "Prefer Pydantic v2 for boundary validation." in line


def test_convention_index_line_truncates_long_body() -> None:
    convention = Convention(name="long", body="A" * 100, tags=[])
    line = convention.index_line()
    assert "..." in line


def test_tags_from_index_line_returns_set() -> None:
    line = "- [foo](conventions/foo.md) [python, async] — body"
    assert Convention.tags_from_index_line(line) == {"python", "async"}


def test_tags_from_index_line_returns_empty_when_no_match() -> None:
    assert Convention.tags_from_index_line("no tags in this line") == set()
