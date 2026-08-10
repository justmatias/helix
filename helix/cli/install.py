"""Install and uninstall the Helix snippet/MCP/hook config for each client."""

import shutil
from pathlib import Path
from typing import Annotated

import typer

from helix.core import Client, Scope, detect_snippet_blocks, install, uninstall
from helix.core.installer import clients as all_clients
from helix.core.installer import (
    detect_installed_clients,
    install_hook,
    install_mcp_config,
    uninstall_hook,
    uninstall_mcp_config,
)

from .prompts import pick, pick_many


def _select_clients(*, keys: list[str] | None, yes: bool) -> list[Client]:
    detected = detect_installed_clients()
    available = detected or all_clients()

    if keys:
        by_key = {client.key: client for client in all_clients()}
        unknown = [key for key in keys if key not in by_key]
        if unknown:
            typer.echo(
                f"Unknown client(s): {', '.join(unknown)}. "
                f"Valid keys: {', '.join(by_key)}.",
                err=True,
            )
            raise typer.Exit(1)
        return [by_key[key] for key in keys]

    if not detected:
        typer.echo("No client config directories found; showing all known clients.")
    if yes:
        return available

    typer.echo("Pick client(s):")
    return [available[i] for i in pick_many("Clients", [c.name for c in available])]


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
    selected = _select_clients(keys=client, yes=yes)

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
            typer.echo(f"Wrote SessionStart hook to {hook_path} ({selected_client.name})")
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
