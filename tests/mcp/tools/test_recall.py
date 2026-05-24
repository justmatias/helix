from collections.abc import Callable

from helix.core import Brain
from helix.mcp.tools.recall import recall


def test_recall_no_match(brain: Brain) -> None:
    assert recall(query="nothing here") == []


def test_recall_finds_match(
    brain: Brain, convention_names: Callable[[list[str]], list[str]]
) -> None:
    brain.remember(name="pydantic", body="Prefer Pydantic v2.", tags=["python"])
    results = recall(query="Pydantic")
    assert "pydantic" in convention_names(results)


def test_recall_filters_by_tag(
    brain: Brain, convention_names: Callable[[list[str]], list[str]]
) -> None:
    brain.remember(name="py-conv", body="Use type hints.", tags=["python"])
    brain.remember(name="ts-conv", body="Use TypeScript strict mode.", tags=["typescript"])
    names = convention_names(recall(query="type", tags=["python"]))
    assert "py-conv" in names
    assert "ts-conv" not in names


def test_recall_filters_by_multiple_tags(
    brain: Brain, convention_names: Callable[[list[str]], list[str]]
) -> None:
    brain.remember(name="py-conv", body="Use type hints.", tags=["python"])
    brain.remember(name="ts-conv", body="Use TypeScript strict mode.", tags=["typescript"])
    brain.remember(name="go-conv", body="Use interfaces.", tags=["go"])
    names = convention_names(recall(query="use", tags=["python", "typescript"]))
    assert "py-conv" in names
    assert "ts-conv" in names
    assert "go-conv" not in names
