from helix.core import Brain
from helix.mcp.tools.recall import recall


def test_recall_no_match() -> None:
    assert recall(query="nothing here") == []


def test_recall_finds_match(brain: Brain) -> None:
    brain.remember(name="pydantic", body="Prefer Pydantic v2.", tags=["python"])
    results = recall(query="Pydantic")
    assert any("pydantic" in r for r in results)


def test_recall_filters_by_tag(brain: Brain) -> None:
    brain.remember(name="py-conv", body="Use type hints.", tags=["python"])
    brain.remember(name="ts-conv", body="Use TypeScript strict mode.", tags=["typescript"])
    results = recall(query="type", tags=["python"])
    assert any("py-conv" in r for r in results)
    assert not any("ts-conv" in r for r in results)


def test_recall_filters_by_multiple_tags(brain: Brain) -> None:
    brain.remember(name="py-conv", body="Use type hints.", tags=["python"])
    brain.remember(name="ts-conv", body="Use TypeScript strict mode.", tags=["typescript"])
    brain.remember(name="go-conv", body="Use interfaces.", tags=["go"])
    results = recall(query="use", tags=["python", "typescript"])
    assert any("py-conv" in r for r in results)
    assert any("ts-conv" in r for r in results)
    assert not any("go-conv" in r for r in results)
