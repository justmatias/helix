from collections.abc import Callable
from typing import Annotated

import typer

from helix.core import Brain
from helix.mcp.app import run_mcp_server
from helix.utils import parse_csv, resolve_text_argument, slugify

from .install import cmd_install, cmd_uninstall

INDEX_HEADER = "# Helix Convention Index"


def cmd_remember(
    body: Annotated[
        str | None,
        typer.Argument(help="Convention body text. Use '-' to read stdin."),
    ] = None,
    name: Annotated[
        str | None,
        typer.Option("--name", "-n", help="Convention name; derived from body if omitted."),
    ] = None,
    tags: Annotated[
        str | None, typer.Option("--tags", "-t", help="Comma-separated tags.")
    ] = None,
) -> None:
    body = resolve_text_argument(body)
    if not body:
        typer.echo("Nothing to remember: empty body.", err=True)
        raise typer.Exit(1)
    brain = Brain()
    resolved = name or brain.free_name(slugify(body))
    path = brain.remember(name=resolved, body=body, tags=parse_csv(tags))
    typer.echo(f"Saved as {path.name}")


def cmd_list(
    tags: Annotated[
        str | None, typer.Option("--tags", "-t", help="Filter by comma-separated tags.")
    ] = None,
) -> None:
    lines = Brain().list_conventions(tags=parse_csv(tags))
    if not lines:
        typer.echo("No conventions found.")
        return
    typer.echo(INDEX_HEADER)
    for line in lines:
        typer.echo(line.rstrip())


def cmd_recall(
    query: Annotated[str, typer.Argument(help="Substring to search for.")],
    tags: Annotated[
        str | None, typer.Option("--tags", "-t", help="Filter by comma-separated tags.")
    ] = None,
) -> None:
    results = Brain().recall(query=query, tags=parse_csv(tags))
    if not results:
        typer.echo("No matches found.")
        return
    typer.echo("\n\n".join(convention.render() for convention in results))


def cmd_edit(
    name: Annotated[str, typer.Argument(help="Convention name to open in $EDITOR.")],
) -> None:
    brain = Brain()
    path = brain.conventions / f"{name}.md"
    if not path.exists():
        typer.echo(f"Convention '{name}' not found.", err=True)
        raise typer.Exit(1)

    typer.edit(filename=str(path))
    if brain.reindex(name):
        typer.echo(f"Updated {path.name}")
        return
    typer.echo(
        f"Warning: {path.name} no longer parses as a convention; index left unchanged.",
        err=True,
    )


def cmd_forget(
    name: Annotated[str, typer.Argument(help="Convention name to remove.")],
) -> None:
    if Brain().forget(name):
        typer.echo(f"Removed {name}")
    else:
        typer.echo(f"Convention '{name}' not found.", err=True)
        raise typer.Exit(1)


def cmd_serve() -> None:  # pragma: no cover
    run_mcp_server()


COMMANDS: dict[str, Callable[..., None]] = {
    "edit": cmd_edit,
    "forget": cmd_forget,
    "install": cmd_install,
    "list": cmd_list,
    "recall": cmd_recall,
    "remember": cmd_remember,
    "serve": cmd_serve,
    "uninstall": cmd_uninstall,
}
