"""Interactive selection helpers for CLI commands."""

import sys

import questionary
import typer


def _interactive() -> bool:
    return sys.stdin.isatty() and sys.stdout.isatty()


def pick(prompt: str, options: list[str]) -> int:
    """Prompt for a single choice and return its zero-based index."""
    if _interactive():  # pragma: no cover - requires a TTY
        choice = questionary.select(prompt, choices=options).ask()
        if choice is None:
            raise typer.Exit(1)
        return options.index(choice)
    return _pick_fallback(prompt, options)


def pick_many(prompt: str, options: list[str]) -> list[int]:
    """Prompt for one or more choices and return their zero-based indices."""
    if _interactive():  # pragma: no cover - requires a TTY
        chosen = questionary.checkbox(prompt, choices=options).ask()
        if chosen is None:
            raise typer.Exit(1)
        return [options.index(c) for c in chosen]
    return _pick_many_fallback(prompt, options)


def _resolve(part: str, options: list[str]) -> int | None:
    """Resolve a user-entered token to a zero-based index, or None if invalid."""
    part = part.strip()
    if part.isdigit():
        index = int(part) - 1
        return index if 0 <= index < len(options) else None
    lowered = part.lower()
    for index, label in enumerate(options):
        if label.lower() == lowered:
            return index
    return None


def _pick_fallback(prompt: str, options: list[str]) -> int:  # pragma: no cover
    typer.echo(prompt)
    for index, label in enumerate(options, 1):
        typer.echo(f"  {index}) {label}")
    raw = typer.prompt(
        f"Enter a number (1-{len(options)}) or the exact option name",
        default="1",
    )
    index = _resolve(str(raw), options)
    if index is None:
        typer.echo(f"Invalid choice: {raw!r}", err=True)
        raise typer.Exit(1)
    return index


def _pick_many_fallback(
    prompt: str, options: list[str]
) -> list[int]:  # pragma: no cover
    typer.echo(prompt)
    for index, label in enumerate(options, 1):
        typer.echo(f"  {index}) {label}")
    raw = typer.prompt(
        f"Enter numbers (1-{len(options)}) or names separated by commas, "
        "or 'all' to select every option",
        default="all",
    )
    if raw.strip().lower() == "all":
        return list(range(len(options)))
    chosen: list[int] = []
    for part in raw.split(","):
        index = _resolve(part, options)
        if index is None:
            typer.echo(f"Invalid choice: {part.strip()!r}", err=True)
            raise typer.Exit(1)
        if index not in chosen:
            chosen.append(index)
    return chosen
