from collections.abc import Callable
from pathlib import Path
from typing import Annotated, cast

import typer

from helix.core import Brain, Scope, detect_installed_blocks, install, uninstall
from helix.core.installer import clients as all_clients
from helix.core.installer import detect_installed_clients
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


def _pick(prompt: str, options: list[str]) -> int:
    for index, label in enumerate(options, 1):
        typer.echo(f"  {index}) {label}")
    choice = typer.prompt(prompt, type=int, default=1)
    if not 1 <= choice <= len(options):
        typer.echo("Invalid choice.", err=True)
        raise typer.Exit(1)
    return choice - 1


def cmd_install() -> None:
    available = detect_installed_clients() or all_clients()
    if not detect_installed_clients():
        typer.echo("No client config directories found; showing all known clients.")

    typer.echo("Pick a client:")
    client = available[_pick("Client", [c.name for c in available])]

    project_root = Path.cwd()
    scope_labels = [
        f"global ({client.global_path})",
        f"project ({client.path_for('project', project_root)})",
    ]
    typer.echo("Pick a scope:")
    scope: Scope = cast(Scope, ("global", "project")[_pick("Scope", scope_labels)])

    path = install(client, scope, project_root)
    typer.echo(f"Wrote helix block to {path}")


def cmd_uninstall() -> None:
    project_root = Path.cwd()
    installed = detect_installed_blocks(project_root)
    if not installed:
        typer.echo("No helix blocks found.")
        return

    typer.echo("Pick a block to remove:")
    labels = [
        f"{client.name} [{scope}] — {client.path_for(scope, project_root)}"
        for client, scope in installed
    ]
    client, scope = installed[_pick("Block", labels)]
    if uninstall(client, scope, project_root):
        typer.echo(f"Removed helix block from {client.path_for(scope, project_root)}")
    else:
        typer.echo("Nothing to remove.", err=True)
        raise typer.Exit(1)


COMMANDS: dict[str, Callable[..., None]] = {
    "forget": cmd_forget,
    "install": cmd_install,
    "list": cmd_list,
    "recall": cmd_recall,
    "remember": cmd_remember,
    "uninstall": cmd_uninstall,
}
