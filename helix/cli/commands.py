import shutil
from collections.abc import Callable
from pathlib import Path
from typing import Annotated

import typer

from helix.core import Brain, Scope, detect_snippet_blocks, install, uninstall
from helix.core.installer import clients as all_clients
from helix.core.installer import detect_installed_clients, install_mcp_config
from helix.mcp.app import run_mcp_server
from helix.utils import parse_csv

from .prompts import pick, pick_many


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


def cmd_install() -> None:
    detected = detect_installed_clients()
    available = detected or all_clients()
    if not detected:
        typer.echo("No client config directories found; showing all known clients.")

    typer.echo("Pick client(s):")
    selected = [available[i] for i in pick_many("Clients", [c.name for c in available])]

    project_root = Path.cwd()
    typer.echo("Pick a scope:")
    scope = (Scope.GLOBAL, Scope.PROJECT)[
        pick("Scope", ["global (per-user config dir)", "project (this repo)"])
    ]

    written: set[Path] = set()
    for client in selected:
        path = client.path_for(scope, project_root)
        if path in written:  # pragma: no cover
            typer.echo(f"Skipped {client.name}: {path} already written this run")
            continue
        install(client, scope, project_root)
        written.add(path)
        typer.echo(f"Wrote helix block to {path} ({client.name})")

        mcp_path = install_mcp_config(client, scope, project_root)
        if mcp_path is not None:
            typer.echo(f"Wrote MCP server config to {mcp_path} ({client.name})")

    if not shutil.which("helix"):  # pragma: no cover
        typer.echo(
            "\nWarning: 'helix' is not on PATH. The installed snippet tells agents "
            "to run `helix list`, which will fail until the CLI is installed on "
            "PATH (e.g. `pipx install helix` or `uv tool install helix`).",
            err=True,
        )


def cmd_serve() -> None:
    run_mcp_server()


def cmd_uninstall() -> None:
    project_root = Path.cwd()
    installed = detect_snippet_blocks(project_root)
    if not installed:
        typer.echo("No helix blocks found.")
        return

    typer.echo("Pick block(s) to remove:")
    labels = [
        f"{block.client.name} [{block.scope}] — {block.path}" for block in installed
    ]
    selected = [installed[i] for i in pick_many("Blocks", labels)]

    removed_any = False
    for block in selected:
        if uninstall(block.client, block.scope, project_root):
            typer.echo(f"Removed helix block from {block.path}")
            removed_any = True
        else:
            typer.echo(f"Nothing to remove from {block.path}", err=True)

    if not removed_any:
        raise typer.Exit(1)


COMMANDS: dict[str, Callable[..., None]] = {
    "forget": cmd_forget,
    "install": cmd_install,
    "list": cmd_list,
    "recall": cmd_recall,
    "remember": cmd_remember,
    "serve": cmd_serve,
    "uninstall": cmd_uninstall,
}
