from collections.abc import Callable
from typing import Annotated

import typer

from helix.core import (
    MergeStrategy,
    SyncError,
    sync_clone,
    sync_init,
    sync_pull,
    sync_push,
)

STRATEGY_HELP = "Conflict resolution: keep-local (default), overwrite, or rename-conflict."


def cmd_sync_init(
    remote_url: Annotated[
        str, typer.Argument(help="Git remote URL to back up conventions to.")
    ],
) -> None:
    try:
        sync_init(remote_url)
    except SyncError as exc:
        typer.echo(str(exc), err=True)
        raise typer.Exit(1) from exc
    typer.echo(f"Configured 'origin' -> {remote_url}")


def cmd_sync_push(
    message: Annotated[
        str, typer.Option("--message", "-m", help="Commit message.")
    ] = "Update conventions",
) -> None:
    try:
        sync_push(message=message)
    except SyncError as exc:
        typer.echo(str(exc), err=True)
        raise typer.Exit(1) from exc
    typer.echo("Pushed conventions to origin.")


def cmd_sync_pull(
    strategy: Annotated[
        MergeStrategy, typer.Option("--strategy", "-s", help=STRATEGY_HELP)
    ] = MergeStrategy.KEEP_LOCAL,
) -> None:
    try:
        result = sync_pull(strategy=strategy)
    except SyncError as exc:
        typer.echo(str(exc), err=True)
        raise typer.Exit(1) from exc
    typer.echo(f"Pulled from origin: {result.summary()}")


def cmd_sync_clone(
    remote_url: Annotated[
        str, typer.Argument(help="Git remote URL to restore conventions from.")
    ],
    strategy: Annotated[
        MergeStrategy, typer.Option("--strategy", "-s", help=STRATEGY_HELP)
    ] = MergeStrategy.KEEP_LOCAL,
) -> None:
    try:
        result = sync_clone(remote_url, strategy=strategy)
    except SyncError as exc:
        typer.echo(str(exc), err=True)
        raise typer.Exit(1) from exc
    typer.echo(f"Cloned from {remote_url}: {result.summary()}")


SYNC_COMMANDS: dict[str, Callable[..., None]] = {
    "clone": cmd_sync_clone,
    "init": cmd_sync_init,
    "pull": cmd_sync_pull,
    "push": cmd_sync_push,
}
