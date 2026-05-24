from collections.abc import Callable

from helix.core import Brain
from helix.mcp.tools.list import list_conventions


def test_list_empty() -> None:
    assert list_conventions() == []


def test_list_returns_convention_names(
    brain: Brain, convention_names: Callable[[list[str]], list[str]]
) -> None:
    brain.remember(name="conv-a", body="Body A.", tags=["python"])
    brain.remember(name="conv-b", body="Body B.", tags=["typescript"])
    names = convention_names(list_conventions())
    assert "conv-a" in names
    assert "conv-b" in names


def test_list_filters_by_single_tag(
    brain: Brain, convention_names: Callable[[list[str]], list[str]]
) -> None:
    brain.remember(name="conv-a", body="Body A.", tags=["python"])
    brain.remember(name="conv-b", body="Body B.", tags=["typescript"])
    names = convention_names(list_conventions(tags=["python"]))
    assert "conv-a" in names
    assert "conv-b" not in names


def test_list_filters_by_multiple_tags(
    brain: Brain, convention_names: Callable[[list[str]], list[str]]
) -> None:
    brain.remember(name="conv-a", body="Body A.", tags=["python"])
    brain.remember(name="conv-b", body="Body B.", tags=["typescript"])
    brain.remember(name="conv-c", body="Body C.", tags=["go"])
    names = convention_names(list_conventions(tags=["python", "typescript"]))
    assert "conv-a" in names
    assert "conv-b" in names
    assert "conv-c" not in names
