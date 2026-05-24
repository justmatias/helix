from helix.core import Brain
from helix.mcp.tools.remember import remember


def test_remember_returns_path_string() -> None:
    result = remember(name="my-conv", body="Always use async.", tags=["python"])
    assert result.endswith("my-conv.md")


def test_remember_persists_convention(brain: Brain) -> None:
    remember(name="my-conv", body="Always use async.", tags=["python"])
    assert any("my-conv" in line for line in brain.list_conventions())


def test_remember_with_tags_and_applies_to(brain: Brain) -> None:
    remember(
        name="typed-conv",
        body="Use type hints.",
        tags=["python"],
        applies_to=["*.py"],
    )
    assert any("typed-conv" in line for line in brain.list_conventions(tags=["python"]))


def test_remember_no_tags(brain: Brain) -> None:
    result = remember(name="untagged", body="Some convention.")
    assert result.endswith("untagged.md")
    assert any("untagged" in line for line in brain.list_conventions())
