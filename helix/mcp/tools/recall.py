from helix.core import Brain
from helix.mcp.app import mcp
from helix.utils import logger, parse_csv


@mcp.tool
def recall(query: str, tags: list[str] | None = None) -> list[str]:
    logger.info(f"recall | query={query!r} tags={tags}")
    results = Brain().recall(query=query, tags=parse_csv(tags))
    logger.info(f"recall | returned {len(results)} result(s)")
    return results
