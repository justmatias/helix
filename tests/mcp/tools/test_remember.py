import pytest

from helix.core import Brain
from helix.mcp import remember


def test_remember_returns_path_string() -> None:
    result = remember(name="my-conv", body="Always use async.", tags=["python"])
    assert result.endswith("my-conv.md")


def test_remember_persists_convention(brain: Brain) -> None:
    remember(name="my-conv", body="Always use async.", tags=["python"])
    assert any("my-conv" in line for line in brain.list_conventions())


def test_remember_with_tags(brain: Brain) -> None:
    remember(name="typed-conv", body="Use type hints.", tags=["python"])
    assert any("typed-conv" in line for line in brain.list_conventions(tags=["python"]))


def test_remember_no_tags(brain: Brain) -> None:
    result = remember(name="untagged", body="Some convention.")
    assert result.endswith("untagged.md")
    assert any("untagged" in line for line in brain.list_conventions())


@pytest.mark.usefixtures("_require_confirm")
def test_remember_require_confirm_previews_without_writing(brain: Brain) -> None:
    result = remember(name="pending", body="Body text.", tags=["python"])
    assert "Confirmation required" in result
    assert "pending.md" in result
    assert "Body text." in result
    assert not (brain.conventions / "pending.md").exists()
    assert not any("pending" in line for line in brain.list_conventions())


@pytest.mark.usefixtures("_require_confirm")
def test_remember_require_confirm_writes_when_confirmed(brain: Brain) -> None:
    result = remember(name="approved", body="Body text.", tags=["python"], confirm=True)
    assert result.endswith("approved.md")
    assert (brain.conventions / "approved.md").exists()
