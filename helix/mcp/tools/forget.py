from helix.core import Brain
from helix.utils import logger

from ._confirm import confirm_gate


def forget(name: str, confirm: bool = False) -> str:
    logger.info(f"forget | name={name}")

    def _preview() -> str | None:
        convention = Brain().convention_for(name)
        if convention is None:
            return None
        logger.info(f"forget | preview only (confirm=False) for {name!r}")
        return (
            "Confirmation required. Re-call `forget` with the same name and "
            "`confirm=True` to delete.\n\n"
            f"Target path: {convention.file_path}"
        )

    def _action() -> str:
        if Brain().forget(name):
            logger.info(f"forget | successfully removed {name!r}")
            return "Successfully forgotten the convention."
        logger.warning(f"forget | convention not found: {name!r}")
        return "I could not find the convention to forget."

    return confirm_gate(confirm, _preview, _action)
