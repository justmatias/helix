import typer

from .utils import initialize_storage

app = typer.Typer()


@app.callback(invoke_without_command=True)
def main(ctx: typer.Context) -> None:
    initialize_storage()
    if ctx.invoked_subcommand is None:
        typer.echo("Helix — global convention memory. Run `helix --help` for commands.")


if __name__ == "__main__":
    app()
