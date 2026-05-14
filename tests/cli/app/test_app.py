from typer.testing import CliRunner

from helix.cli import app
from helix.core import Brain


def test_main_callback_initializes_brain(
    runner: CliRunner,
    brain: Brain,
) -> None:
    result = runner.invoke(app, [])
    assert result.exit_code == 0
    assert "Helix" in result.stdout
    assert brain.is_initialized
