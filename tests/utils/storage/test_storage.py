from helix.settings import Settings
from helix.utils.storage import initialize_storage


def test_initialize_storage_creates_conventions_dir() -> None:
    assert not Settings.HELIX_CONVENTIONS.is_dir()
    initialize_storage()
    assert Settings.HELIX_CONVENTIONS.is_dir()


def test_initialize_storage_creates_index_file() -> None:
    assert not Settings.HELIX_INDEX.exists()
    initialize_storage()
    assert Settings.HELIX_INDEX.exists()
    assert Settings.HELIX_INDEX.read_text() == "# Helix Convention Index\n\n"


def test_initialize_storage_does_not_overwrite_existing_index() -> None:
    Settings.HELIX_CONVENTIONS.mkdir(parents=True, exist_ok=True)
    Settings.HELIX_INDEX.write_text("existing content")

    initialize_storage()

    assert Settings.HELIX_INDEX.read_text() == "existing content"


def test_initialize_storage_is_idempotent() -> None:
    initialize_storage()
    initialize_storage()

    assert Settings.HELIX_CONVENTIONS.is_dir()
    assert Settings.HELIX_INDEX.read_text() == "# Helix Convention Index\n\n"
