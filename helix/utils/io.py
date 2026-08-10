import sys

import typer


def resolve_text_argument(value: str | None) -> str:
    """Read text from ``value``, or stdin if ``'-'``, or $EDITOR if omitted."""
    if value == "-":
        value = sys.stdin.read()
    elif value is None:
        value = typer.edit("") or ""
    return value.strip()
