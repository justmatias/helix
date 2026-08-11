from typing import Annotated

import typer

from helix import __version__
from helix.core import Brain

from .commands import COMMANDS

app = typer.Typer()


def _version_callback(value: bool) -> None:
    if value:
        typer.echo(f"helix {__version__}")
        raise typer.Exit()


@app.callback(invoke_without_command=True)
def main(
    ctx: typer.Context,
    version: Annotated[
        bool,
        typer.Option(
            "--version",
            callback=_version_callback,
            is_eager=True,
            help="Show the installed version and exit.",
        ),
    ] = False,
) -> None:
    Brain().initialize()
    if ctx.invoked_subcommand is None:
        typer.echo("Helix — global convention memory. Run `helix --help` for commands.")


for name, command in COMMANDS.items():
    app.command(name)(command)


if __name__ == "__main__":  # pragma: no cover
    app()
