import sys
from collections.abc import Callable

import typer

from helix.core import InvalidConfigError


def resolve_text_argument(value: str | None) -> str:
    """Read text from ``value``, or stdin if ``'-'``, or $EDITOR if omitted."""
    if value == "-":
        value = sys.stdin.read()
    elif value is None:
        value = typer.edit("") or ""
    return value.strip()


def warn_on_invalid_config[T](func: Callable[..., T], **kwargs: object) -> T | None:
    """Call ``func(**kwargs)``, echoing and swallowing an ``InvalidConfigError``."""
    try:
        return func(**kwargs)
    except InvalidConfigError as exc:
        typer.echo(str(exc), err=True)
        return None
