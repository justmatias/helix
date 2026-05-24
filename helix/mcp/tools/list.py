from helix.core import Brain
from helix.utils import logger


def list_conventions(tags: list[str] | None = None) -> list[str]:
    logger.info(f"list_conventions | tags={tags}")
    results = Brain().list_conventions(tags=tags)
    logger.info(f"list_conventions | returned {len(results)} convention(s)")
    return results
