import typer

from helix.cli.commands import COMMANDS
from helix.core import Brain

app = typer.Typer()


@app.callback(invoke_without_command=True)
def main(ctx: typer.Context) -> None:
    Brain().initialize()
    if ctx.invoked_subcommand is None:
        typer.echo("Helix — global convention memory. Run `helix --help` for commands.")


for name, command in COMMANDS.items():
    app.command(name)(command)


if __name__ == "__main__":  # pragma: no cover
    app()
