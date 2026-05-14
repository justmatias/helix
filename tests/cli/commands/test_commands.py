import pytest
import typer

from helix.cli import cmd_forget, cmd_list, cmd_recall, cmd_remember
from helix.core import Brain


def test_cmd_remember_creates_file_and_echoes(
    capsys: pytest.CaptureFixture[str],
) -> None:
    cmd_remember(
        body="Always use async.",
        name="my-conv",
        tags="python,async",
        applies_to=None,
    )
    captured = capsys.readouterr()
    assert "Saved as my-conv.md" in captured.out
    assert (Brain().conventions / "my-conv.md").exists()


def test_cmd_list_empty(capsys: pytest.CaptureFixture[str]) -> None:
    cmd_list(tags=None)
    captured = capsys.readouterr()
    assert "No conventions found." in captured.out


def test_cmd_list_shows_entries(capsys: pytest.CaptureFixture[str]) -> None:
    Brain().remember(name="conv-a", body="Body A.", tags=["python"])
    cmd_list(tags=None)
    captured = capsys.readouterr()
    assert "conv-a" in captured.out


def test_cmd_list_filters_by_tags(capsys: pytest.CaptureFixture[str]) -> None:
    Brain().remember(name="conv-a", body="Body A.", tags=["python"])
    Brain().remember(name="conv-b", body="Body B.", tags=["typescript"])
    cmd_list(tags="python")
    captured = capsys.readouterr()
    assert "conv-a" in captured.out
    assert "conv-b" not in captured.out


def test_cmd_recall_no_match(capsys: pytest.CaptureFixture[str]) -> None:
    cmd_recall(query="nothing", tags=None)
    captured = capsys.readouterr()
    assert "No matches found." in captured.out


def test_cmd_recall_finds_match(capsys: pytest.CaptureFixture[str]) -> None:
    Brain().remember(name="pydantic", body="Prefer Pydantic v2.", tags=["python"])
    cmd_recall(query="Pydantic", tags=None)
    captured = capsys.readouterr()
    assert "pydantic" in captured.out


def test_cmd_forget_removes(capsys: pytest.CaptureFixture[str]) -> None:
    Brain().remember(name="to-delete", body="Body.", tags=["misc"])
    cmd_forget(name="to-delete")
    captured = capsys.readouterr()
    assert "Removed to-delete" in captured.out


def test_cmd_forget_missing_exits(capsys: pytest.CaptureFixture[str]) -> None:
    with pytest.raises(typer.Exit) as exc:
        cmd_forget(name="nonexistent")
    assert exc.value.exit_code == 1
    captured = capsys.readouterr()
    assert "not found" in captured.err
