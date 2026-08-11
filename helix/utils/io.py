import functools
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


def warn_on_invalid_config[T](func: Callable[..., T]) -> Callable[..., T | None]:
    """Wrap ``func`` so an ``InvalidConfigError`` it raises is echoed and swallowed.

    Installer functions raise ``InvalidConfigError`` on a malformed client config
    file; the CLI is the boundary that should report it and move on rather than
    crash with a traceback.
    """

    @functools.wraps(func)
    def safe(*args: object, **kwargs: object) -> T | None:
        try:
            return func(*args, **kwargs)
        except InvalidConfigError as exc:
            typer.echo(str(exc), err=True)
            return None

    return safe
