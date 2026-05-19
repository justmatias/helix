import shutil
from collections.abc import Callable
from pathlib import Path
from typing import Annotated

import typer

from helix.core import Brain, Scope, detect_snippet_blocks, install, uninstall
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
    return int(choice) - 1


def _pick_many(prompt: str, options: list[str]) -> list[int]:
    for index, label in enumerate(options, 1):
        typer.echo(f"  {index}) {label}")
    raw = typer.prompt(f"{prompt} (comma-separated, or 'all')", default="all")
    if raw.strip().lower() == "all":
        return list(range(len(options)))
    chosen: list[int] = []
    for raw_part in raw.split(","):
        part = raw_part.strip()
        if not part.isdigit() or not 1 <= int(part) <= len(options):
            typer.echo(f"Invalid choice: {part!r}", err=True)
            raise typer.Exit(1)
        index = int(part) - 1
        if index not in chosen:
            chosen.append(index)
    return chosen


def cmd_install() -> None:
    detected = detect_installed_clients()
    available = detected or all_clients()
    if not detected:
        typer.echo("No client config directories found; showing all known clients.")

    typer.echo("Pick client(s):")
    selected = [
        available[i] for i in _pick_many("Clients", [c.name for c in available])
    ]

    project_root = Path.cwd()
    typer.echo("Pick a scope:")
    scope = (Scope.GLOBAL, Scope.PROJECT)[
        _pick("Scope", ["global (per-user config dir)", "project (this repo)"])
    ]

    written: set[Path] = set()
    for client in selected:
        path = client.path_for(scope, project_root)
        if path in written:
            typer.echo(f"Skipped {client.name}: {path} already written this run")
            continue
        install(client, scope, project_root)
        written.add(path)
        typer.echo(f"Wrote helix block to {path} ({client.name})")

    if shutil.which("helix") is None:
        typer.echo(
            "\nWarning: 'helix' is not on PATH. The installed snippet tells agents "
            "to run `helix list`, which will fail until the CLI is installed on "
            "PATH (e.g. `pipx install helix` or `uv tool install helix`).",
            err=True,
        )


def cmd_uninstall() -> None:
    project_root = Path.cwd()
    installed = detect_snippet_blocks(project_root)
    if not installed:
        typer.echo("No helix blocks found.")
        return

    typer.echo("Pick a block to remove:")
    labels = [
        f"{block.client.name} [{block.scope}] — {block.path}" for block in installed
    ]
    block = installed[_pick("Block", labels)]
    if uninstall(block.client, block.scope, project_root):
        typer.echo(f"Removed helix block from {block.path}")
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
