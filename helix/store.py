from pathlib import Path

BRAIN_DIR = Path.home() / ".dev_brain"
CONVENTIONS_DIR = BRAIN_DIR / "conventions"
INDEX_FILE = BRAIN_DIR / "INDEX.md"


def init_store() -> None:
    """Create ~/.dev_brain/ skeleton if it doesn't exist."""
    CONVENTIONS_DIR.mkdir(parents=True, exist_ok=True)
    if not INDEX_FILE.exists():
        INDEX_FILE.write_text("# Helix Convention Index\n\n")
