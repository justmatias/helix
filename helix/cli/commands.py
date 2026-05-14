from collections.abc import Callable
from typing import Annotated

import typer

from helix.core import Brain
from helix.utils import parse_csv


def cmd_remember(
    name: Annotated[str, typer.Argument(help="Convention name (kebab-case).")],
    body: Annotated[str, typer.Argument(help="Convention body text.")],
    tags: Annotated[str | None, typer.Option(help="Comma-separated tags.")] = None,
    applies_to: Annotated[
        str | None, typer.Option(help="Comma-separated stacks/scopes.")
    ] = None,
) -> None:
    path = Brain().remember(
        name=name,
        body=body,
        tags=parse_csv(tags),
        applies_to=parse_csv(applies_to),
    )
    typer.echo(f"Saved as {path.name}")


def cmd_list(
    tags: Annotated[
        str | None, typer.Option(help="Filter by comma-separated tags.")
    ] = None,
) -> None:
    lines = Brain().list_conventions(tags=parse_csv(tags))
    if not lines:
        typer.echo("No conventions found.")
        return
    for line in lines:
        typer.echo(line)


def cmd_recall(
    query: Annotated[str, typer.Argument(help="Substring to search for.")],
    tags: Annotated[
        str | None, typer.Option(help="Filter by comma-separated tags.")
    ] = None,
) -> None:
    results: list[str] = Brain().recall(query=query, tags=parse_csv(tags))
    if not results:
        typer.echo("No matches found.")
        return
    for line in results:
        typer.echo(line)


def cmd_forget(
    name: Annotated[str, typer.Argument(help="Convention name to remove.")],
) -> None:
    if Brain().forget(name):
        typer.echo(f"Removed {name}")
    else:
        typer.echo(f"Convention '{name}' not found.", err=True)
        raise typer.Exit(1)


COMMANDS: dict[str, Callable[..., None]] = {
    "forget": cmd_forget,
    "list": cmd_list,
    "recall": cmd_recall,
    "remember": cmd_remember,
}
