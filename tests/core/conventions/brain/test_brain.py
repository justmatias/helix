import pytest

from helix.core import Brain


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
def test_convention_for_returns_none_when_invalid(brain: Brain) -> None:
    (brain.conventions / "broken.md").write_text("---\ntags: [python]\n---\nBody.\n")
    assert brain.convention_for("broken") is None


def test_list_conventions_returns_empty_when_not_initialized(brain: Brain) -> None:
    assert not brain.is_initialized
    assert brain.list_conventions() == []


@pytest.mark.usefixtures("_initialize_brain")
def test_recall_skips_invalid_convention_files(brain: Brain) -> None:
    brain.remember(name="valid", body="Has thing.", tags=["python"])
    (brain.conventions / "broken.md").write_text("---\ntags: [python]\n---\nthing.\n")
    results = brain.recall("thing", tags=["python"])
    assert [convention.name for convention in results] == ["valid"]


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
    assert [convention.name for convention in results] == ["pydantic"]
    assert results[0].body == "Prefer Pydantic v2 for validation."


@pytest.mark.usefixtures("_initialize_brain")
def test_recall_no_match(brain: Brain) -> None:
    brain.remember(name="pydantic", body="Prefer Pydantic v2.", tags=["python"])
    assert brain.recall("xyzzy_no_match_9999") == []


@pytest.mark.usefixtures("_initialize_brain")
def test_recall_filter_by_tag_excludes_other_stacks(brain: Brain) -> None:
    brain.remember(name="py-conv", body="Python thing.", tags=["python"])
    brain.remember(name="ts-conv", body="TypeScript thing.", tags=["typescript"])
    results = brain.recall("thing", tags=["python"])
    assert [convention.name for convention in results] == ["py-conv"]


@pytest.mark.usefixtures("_initialize_brain")
def test_recall_matches_name_and_tags(brain: Brain) -> None:
    brain.remember(name="pydantic", body="Nothing relevant here.", tags=["python"])
    assert [c.name for c in brain.recall("pydantic")] == ["pydantic"]
    assert [c.name for c in brain.recall("python")] == ["pydantic"]


@pytest.mark.usefixtures("_initialize_brain")
def test_recall_returns_each_convention_once(brain: Brain) -> None:
    brain.remember(name="repeat", body="thing thing thing", tags=["python"])
    assert len(brain.recall("thing")) == 1


@pytest.mark.usefixtures("_initialize_brain")
def test_free_name_returns_name_when_available(brain: Brain) -> None:
    assert brain.free_name("fresh") == "fresh"


@pytest.mark.usefixtures("_initialize_brain")
def test_free_name_suffixes_on_collision(brain: Brain) -> None:
    brain.remember(name="taken", body="One.", tags=[])
    assert brain.free_name("taken") == "taken-2"
    brain.remember(name="taken-2", body="Two.", tags=[])
    assert brain.free_name("taken") == "taken-3"


@pytest.mark.usefixtures("_initialize_brain")
def test_reindex_refreshes_index_line(brain: Brain) -> None:
    brain.remember(name="edited", body="Old body.", tags=["python"])
    (brain.conventions / "edited.md").write_text(
        "---\nname: edited\ntags: [python]\n---\n\nNew body.\n"
    )
    assert brain.reindex("edited")
    assert "New body." in brain.index.read_text()
    assert "Old body." not in brain.index.read_text()


@pytest.mark.usefixtures("_initialize_brain")
def test_reindex_returns_false_for_invalid_file(brain: Brain) -> None:
    (brain.conventions / "broken.md").write_text("---\ntags: [python]\n---\nBody.\n")
    assert not brain.reindex("broken")


@pytest.mark.usefixtures("_initialize_brain")
def test_rebuild_index_reflects_files_written_directly_to_disk(brain: Brain) -> None:
    (brain.conventions / "manual.md").write_text(
        "---\nname: manual\ntags: [python]\n---\n\nAdded outside of remember().\n"
    )
    brain.rebuild_index()
    assert "manual" in brain.index.read_text()


@pytest.mark.usefixtures("_initialize_brain")
def test_rebuild_index_drops_entries_for_deleted_files(brain: Brain) -> None:
    brain.remember(name="to-delete", body="Delete me.", tags=["misc"])
    (brain.conventions / "to-delete.md").unlink()
    brain.rebuild_index()
    assert "to-delete" not in brain.index.read_text()


@pytest.mark.usefixtures("_initialize_brain")
def test_rebuild_index_skips_invalid_convention_files(brain: Brain) -> None:
    brain.remember(name="valid", body="Body.", tags=["python"])
    (brain.conventions / "broken.md").write_text("---\ntags: [python]\n---\nBody.\n")
    brain.rebuild_index()
    assert "valid" in brain.index.read_text()
    assert "broken" not in brain.index.read_text()


def test_rebuild_index_creates_conventions_dir_when_missing(brain: Brain) -> None:
    assert not brain.conventions.is_dir()
    brain.rebuild_index()
    assert brain.conventions.is_dir()
