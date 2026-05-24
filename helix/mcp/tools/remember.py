from helix.core import Brain
from helix.mcp.app import mcp
from helix.utils import logger, parse_csv


@mcp.tool
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
        tags=parse_csv(tags),
        applies_to=parse_csv(applies_to),
    )
    logger.info(f"remember | saved to {path}")
    return str(path)
