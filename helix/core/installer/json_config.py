import json
from pathlib import Path

from .errors import InvalidConfigError


def read_json(path: Path, text: str) -> dict:
    """Parse ``text`` (the contents of ``path``) as JSON, or {} if blank."""
    if not text.strip():
        return {}
    try:
        data: dict = json.loads(text)
        return data
    except json.JSONDecodeError as exc:
        raise InvalidConfigError(f"{path} is not valid JSON: {exc}") from exc
