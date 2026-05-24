from helix.core import Brain
from helix.core.settings import Settings
from helix.utils import logger


def forget(name: str, confirm: bool = False) -> str:
    logger.info(f"forget | name={name}")

    if Settings.HELIX_REQUIRE_CONFIRM and not confirm:
        brain = Brain()
        convention = brain.convention_for(name)
        if convention is None:
            logger.warning(f"forget | convention not found: {name!r}")
            return "I could not find the convention to forget."
        logger.info(f"forget | preview only (confirm=False) for {name!r}")
        return (
            "Confirmation required. Re-call `forget` with the same name and "
            "`confirm=True` to delete.\n\n"
            f"Target path: {convention.file_path}"
        )

    has_forgotten = Brain().forget(name)
    if has_forgotten:
        logger.info(f"forget | successfully removed {name!r}")
        return "Successfully forgotten the convention."
    logger.warning(f"forget | convention not found: {name!r}")
    return "I could not find the convention to forget."
