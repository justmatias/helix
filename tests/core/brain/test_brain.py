import pytest

from helix.core.brain import Brain


def test_initialize_creates_conventions_dir(brain: Brain) -> None:
    assert not brain.conventions.is_dir()
    brain.initialize()
    assert brain.conventions.is_dir()


def test_initialize_creates_index_file(brain: Brain) -> None:
    assert not brain.index.exists()
    brain.initialize()
    assert brain.index.exists()
    assert brain.index.read_text() == "# Helix Convention Index\n\n"


def test_initialize_does_not_overwrite_existing_index(brain: Brain) -> None:
    brain.conventions.mkdir(parents=True, exist_ok=True)
    brain.index.write_text("existing content")
    brain.initialize()
    assert brain.index.read_text() == "existing content"


def test_initialize_is_idempotent(brain: Brain) -> None:
    brain.initialize()
    brain.initialize()
    assert brain.conventions.is_dir()
    assert brain.index.read_text() == "# Helix Convention Index\n\n"


@pytest.mark.usefixtures("_initialize_brain")
def test_remember_creates_convention_file(brain: Brain) -> None:
    assert not (brain.conventions / "my-conv.md").exists()
    brain.remember(name="my-conv", body="Always use async.", tags=["python"])
    assert (brain.conventions / "my-conv.md").exists()


@pytest.mark.usefixtures("_initialize_brain")
def test_remember_file_contains_body(brain: Brain) -> None:
    brain.remember(name="my-conv", body="Always use async.", tags=["python"])
    assert "Always use async." in (brain.conventions / "my-conv.md").read_text()


@pytest.mark.usefixtures("_initialize_brain")
def test_remember_appends_to_index(brain: Brain) -> None:
    brain.remember(name="my-conv", body="Always use async.", tags=["python"])
    assert "my-conv" in brain.index.read_text()


@pytest.mark.usefixtures("_initialize_brain")
def test_remember_overwrites_existing_file(brain: Brain) -> None:
    brain.remember(name="my-conv", body="Version 1.", tags=["python"])
    brain.remember(name="my-conv", body="Version 2.", tags=["python"])
    content = (brain.conventions / "my-conv.md").read_text()
    assert "Version 2." in content
    assert "Version 1." not in content


@pytest.mark.usefixtures("_initialize_brain")
def test_remember_overwrites_keeps_single_index_entry(brain: Brain) -> None:
    brain.remember(name="my-conv", body="Version 1.", tags=["python"])
    brain.remember(name="my-conv", body="Version 2.", tags=["python"])
    assert len(brain.list_conventions()) == 1


@pytest.mark.usefixtures("_initialize_brain")
def test_list_conventions_empty(brain: Brain) -> None:
    assert brain.list_conventions() == []


@pytest.mark.usefixtures("_initialize_brain")
def test_list_conventions_returns_all(brain: Brain) -> None:
    assert len(brain.list_conventions()) == 0
    brain.remember(name="conv-a", body="Body A.", tags=["python"])
    brain.remember(name="conv-b", body="Body B.", tags=["typescript"])
    assert len(brain.list_conventions()) == 2


@pytest.mark.usefixtures("_initialize_brain")
def test_list_conventions_filter_by_tag(brain: Brain) -> None:
    brain.remember(name="conv-a", body="Body A.", tags=["python"])
    brain.remember(name="conv-b", body="Body B.", tags=["typescript"])
    lines = brain.list_conventions(tags=["python"])
    assert len(lines) == 1
    assert "conv-a" in lines[0]


@pytest.mark.usefixtures("_initialize_brain")
def test_list_conventions_filter_no_match(brain: Brain) -> None:
    brain.remember(name="conv-a", body="Body A.", tags=["python"])
    assert brain.list_conventions(tags=["rust"]) == []


@pytest.mark.usefixtures("_initialize_brain")
def test_index_line_for_returns_line(brain: Brain) -> None:
    brain.remember(name="my-conv", body="Always use async.", tags=["python"])
    line = brain.index_line_for("my-conv")
    assert line is not None
    assert "my-conv" in line


@pytest.mark.usefixtures("_initialize_brain")
def test_index_line_for_returns_none_when_missing(brain: Brain) -> None:
    assert brain.index_line_for("nonexistent") is None


@pytest.mark.usefixtures("_initialize_brain")
def test_convention_for_returns_convention(brain: Brain) -> None:
    brain.remember(name="pydantic", body="Prefer Pydantic v2.", tags=["python"])
    convention = brain.convention_for("pydantic")
    assert convention is not None
    assert convention.name == "pydantic"
    assert convention.body == "Prefer Pydantic v2."
    assert convention.tags == ["python"]


@pytest.mark.usefixtures("_initialize_brain")
def test_convention_for_returns_none_when_missing(brain: Brain) -> None:
    assert brain.convention_for("nonexistent") is None


@pytest.mark.usefixtures("_initialize_brain")
def test_forget_removes_file(brain: Brain) -> None:
    brain.remember(name="to-delete", body="Delete me.", tags=["misc"])
    assert brain.forget("to-delete")
    assert not (brain.conventions / "to-delete.md").exists()


@pytest.mark.usefixtures("_initialize_brain")
def test_forget_removes_from_index(brain: Brain) -> None:
    brain.remember(name="to-delete", body="Delete me.", tags=["misc"])
    brain.forget("to-delete")
    assert "to-delete" not in brain.index.read_text()


@pytest.mark.usefixtures("_initialize_brain")
def test_forget_returns_false_for_nonexistent(brain: Brain) -> None:
    assert not brain.forget("nonexistent")


@pytest.mark.usefixtures("_initialize_brain")
def test_recall_finds_match(brain: Brain) -> None:
    brain.remember(
        name="pydantic", body="Prefer Pydantic v2 for validation.", tags=["python"]
    )
    results = brain.recall("Pydantic")
    assert len(results) > 0
    assert any("pydantic" in result for result in results)


@pytest.mark.usefixtures("_initialize_brain")
def test_recall_no_match(brain: Brain) -> None:
    brain.remember(name="pydantic", body="Prefer Pydantic v2.", tags=["python"])
    assert brain.recall("xyzzy_no_match_9999") == []


@pytest.mark.usefixtures("_initialize_brain")
def test_recall_filter_by_tag_excludes_other_stacks(brain: Brain) -> None:
    brain.remember(name="py-conv", body="Python thing.", tags=["python"])
    brain.remember(name="ts-conv", body="TypeScript thing.", tags=["typescript"])
    results = brain.recall("thing", tags=["python"])
    assert any("py-conv" in result for result in results)
    assert not any("ts-conv" in result for result in results)
