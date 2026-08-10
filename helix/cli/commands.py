import shutil
from collections.abc import Callable
from pathlib import Path
from typing import Annotated

import typer

from helix.core import Brain, Scope, detect_snippet_blocks, install, uninstall
from helix.core.installer import (
    install_hook,
    install_mcp_config,
    uninstall_hook,
    uninstall_mcp_config,
)
from helix.mcp.app import run_mcp_server
from helix.utils import parse_csv, resolve_text_argument, slugify

from .prompts import pick, pick_many, select_clients

INDEX_HEADER = "# Helix Convention Index"


def cmd_remember(
    body: Annotated[
        str | None,
        typer.Argument(help="Convention body text. Use '-' to read stdin."),
    ] = None,
    name: Annotated[
        str | None,
        typer.Option(
            "--name", "-n", help="Convention name; derived from body if omitted."
        ),
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


def cmd_install(
    client: Annotated[
        list[str] | None,
        typer.Option("--client", "-c", help="Client key (repeatable), e.g. 'claude'."),
    ] = None,
    scope: Annotated[
        Scope | None, typer.Option("--scope", "-s", help="Install scope.")
    ] = None,
    yes: Annotated[
        bool, typer.Option("--yes", "-y", help="Skip prompts; accept defaults.")
    ] = False,
) -> None:
    selected = select_clients(keys=client, yes=yes)

    if scope is None:
        if yes:
            scope = Scope.GLOBAL
        else:
            typer.echo("Pick a scope:")
            scope = (Scope.GLOBAL, Scope.PROJECT)[
                pick("Scope", ["global (per-user config dir)", "project (this repo)"])
            ]

    project_root = Path.cwd()
    written: set[Path] = set()
    hooked = False
    for selected_client in selected:
        path = selected_client.path_for(scope, project_root)
        if path in written:  # pragma: no cover
            typer.echo(f"Skipped {selected_client.name}: {path} already written")
            continue
        install(selected_client, scope, project_root)
        written.add(path)
        typer.echo(f"Wrote helix block to {path} ({selected_client.name})")

        mcp_path = install_mcp_config(selected_client, scope, project_root)
        if mcp_path is not None:
            typer.echo(
                f"Wrote MCP server config to {mcp_path} ({selected_client.name})"
            )

        hook_path = install_hook(selected_client, scope, project_root)
        if hook_path is not None:
            typer.echo(
                f"Wrote SessionStart hook to {hook_path} ({selected_client.name})"
            )
            hooked = True

    if hooked:
        typer.echo("\nRestart your client for the SessionStart hook to take effect.")

    if not shutil.which("helix"):  # pragma: no cover
        typer.echo(
            "\nWarning: 'helix' is not on PATH. The installed snippet tells agents "
            "to run `helix list`, which will fail until the CLI is installed on "
            "PATH (e.g. `pipx install helix` or `uv tool install helix`).",
            err=True,
        )


def cmd_serve() -> None:  # pragma: no cover
    run_mcp_server()


def cmd_uninstall(
    yes: Annotated[
        bool, typer.Option("--yes", "-y", help="Remove every detected block.")
    ] = False,
) -> None:
    project_root = Path.cwd()
    installed = detect_snippet_blocks(project_root)
    if not installed:
        typer.echo("No helix blocks found.")
        return

    if yes:
        selected = installed
    else:
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

        if uninstall_mcp_config(block.client, block.scope, project_root):
            typer.echo(f"Removed MCP server config for {block.client.name}")

        if uninstall_hook(block.client, block.scope, project_root):
            typer.echo(f"Removed SessionStart hook for {block.client.name}")

    if not removed_any:
        raise typer.Exit(1)


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
