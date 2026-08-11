from typer.testing import CliRunner

from helix import __version__
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


def test_version_flag_prints_version_and_exits(runner: CliRunner) -> None:
    result = runner.invoke(app, ["--version"])
    assert result.exit_code == 0
    assert result.stdout.strip() == f"helix {__version__}"
