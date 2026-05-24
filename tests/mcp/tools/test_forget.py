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
