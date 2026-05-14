import typer

from helix.core import Brain
from helix.utils import parse_csv


def cmd_remember(
    *,
    body: str,
    name: str,
    tags: str | None,
    applies_to: str | None,
) -> None:
    path = Brain().remember(
        name=name,
        body=body,
        tags=parse_csv(tags),
        applies_to=parse_csv(applies_to),
    )
    typer.echo(f"Saved as {path.name}")


def cmd_list(*, tags: str | None) -> None:
    lines = Brain().list_conventions(tags=parse_csv(tags))
    if not lines:
        typer.echo("No conventions found.")
        return
    for line in lines:
        typer.echo(line)


def cmd_recall(*, query: str, tags: str | None) -> None:
    results: list[str] = Brain().recall(query=query, tags=parse_csv(tags))
    if not results:
        typer.echo("No matches found.")
        return
    for line in results:
        typer.echo(line)


def cmd_forget(*, name: str) -> None:
    if Brain().forget(name):
        typer.echo(f"Removed {name}")
    else:
        typer.echo(f"Convention '{name}' not found.", err=True)
        raise typer.Exit(1)
