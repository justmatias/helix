from helix.core import Brain
from helix.utils import logger


def forget(name: str) -> str:
    logger.info(f"forget | name={name}")
    has_forgotten = Brain().forget(name)
    if has_forgotten:
        logger.info(f"forget | successfully removed {name!r}")
        return "Successfully forgotten the convention."
    logger.warning(f"forget | convention not found: {name!r}")
    return "I could not find the convention to forget."
