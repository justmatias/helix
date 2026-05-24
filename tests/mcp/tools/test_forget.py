import pytest

from helix.core import Brain
from helix.mcp.tools.forget import forget


def test_forget_removes_convention(brain: Brain) -> None:
    brain.remember(name="to-delete", body="Body.", tags=["misc"])
    result = forget(name="to-delete")
    assert result == "Successfully forgotten the convention."
    assert "to-delete" not in brain.list_conventions()


def test_forget_missing_convention() -> None:
    result = forget(name="nonexistent")
    assert result == "I could not find the convention to forget."


@pytest.mark.usefixtures("_require_confirm")
def test_forget_require_confirm_previews_without_deleting(brain: Brain) -> None:
    brain.remember(name="pending-delete", body="Body.", tags=["misc"])
    result = forget(name="pending-delete")
    assert "Confirmation required" in result
    assert "pending-delete.md" in result
    assert (brain.conventions / "pending-delete.md").exists()


@pytest.mark.usefixtures("_require_confirm")
def test_forget_require_confirm_missing_returns_not_found() -> None:
    result = forget(name="nonexistent")
    assert result == "I could not find the convention to forget."


@pytest.mark.usefixtures("_require_confirm")
def test_forget_require_confirm_deletes_when_confirmed(brain: Brain) -> None:
    brain.remember(name="approved-delete", body="Body.", tags=["misc"])
    result = forget(name="approved-delete", confirm=True)
    assert result == "Successfully forgotten the convention."
    assert not (brain.conventions / "approved-delete.md").exists()
