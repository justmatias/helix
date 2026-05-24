from helix.core import Brain
from helix.utils import logger


def remember(
    name: str,
    body: str,
    tags: list[str] | None = None,
    applies_to: list[str] | None = None,
) -> str:
    logger.info(f"remember | name={name} tags={tags} applies_to={applies_to}")
    path = Brain().remember(
        name=name,
        body=body,
        tags=tags or [],
        applies_to=applies_to,
    )
    logger.info(f"remember | saved to {path}")
    return str(path)
