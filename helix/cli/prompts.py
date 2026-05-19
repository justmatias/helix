"""Interactive selection helpers for CLI commands."""

import typer


def pick(prompt: str, options: list[str]) -> int:  # pragma: no cover
    """Prompt for a single choice and return its zero-based index."""
    for index, label in enumerate(options, 1):
        typer.echo(f"  {index}) {label}")
    choice = typer.prompt(prompt, type=int, default=1)
    if not 1 <= choice <= len(options):
        typer.echo("Invalid choice.", err=True)
        raise typer.Exit(1)
    return int(choice) - 1


def pick_many(prompt: str, options: list[str]) -> list[int]:  # pragma: no cover
    """Prompt for one or more choices and return their zero-based indices."""
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
