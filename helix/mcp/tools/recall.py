from helix.core import Brain
from helix.utils import logger


def recall(query: str, tags: list[str] | None = None) -> list[str]:
    logger.info(f"recall | query={query!r} tags={tags}")
    results = Brain().recall(query=query, tags=tags)
    logger.info(f"recall | returned {len(results)} result(s)")
    return results
