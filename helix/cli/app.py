import typer

from helix.core import Brain

from .commands import COMMANDS
from .sync import SYNC_COMMANDS

app = typer.Typer()
sync_app = typer.Typer(help="Backup and sync conventions with a remote git repository.")


@app.callback(invoke_without_command=True)
def main(ctx: typer.Context) -> None:
    Brain().initialize()
    if ctx.invoked_subcommand is None:
        typer.echo("Helix — global convention memory. Run `helix --help` for commands.")


for name, command in COMMANDS.items():
    app.command(name)(command)

for name, command in SYNC_COMMANDS.items():
    sync_app.command(name)(command)

app.add_typer(sync_app, name="sync")


if __name__ == "__main__":  # pragma: no cover
    app()
