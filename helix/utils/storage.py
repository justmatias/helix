from helix.settings import Settings


def initialize_storage() -> None:
    """Create ~/.dev_brain/ skeleton if it doesn't exist."""
    Settings.HELIX_CONVENTIONS.mkdir(parents=True, exist_ok=True)
    if not Settings.HELIX_INDEX.exists():
        Settings.HELIX_INDEX.write_text("# Helix Convention Index\n\n")
