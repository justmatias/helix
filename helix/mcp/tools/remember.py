from helix.core import Brain
from helix.core.conventions.convention import Convention
from helix.core.settings import Settings
from helix.utils import logger


def remember(
    name: str,
    body: str,
    tags: list[str] | None = None,
    applies_to: list[str] | None = None,
    confirm: bool = False,
) -> str:
    logger.info(f"remember | name={name} tags={tags} applies_to={applies_to}")

    if Settings.HELIX_REQUIRE_CONFIRM and not confirm:
        preview = Convention(
            name=name,
            body=body,
            tags=tags or [],
            applies_to=applies_to or [],
        )
        logger.info(f"remember | preview only (confirm=False) for {name!r}")
        return (
            "Confirmation required. Re-call `remember` with the same arguments and "
            "`confirm=True` to write.\n\n"
            f"Target path: {preview.file_path}\n\n"
            "--- file contents ---\n"
            f"{preview.to_markdown()}"
        )

    path = Brain().remember(
        name=name,
        body=body,
        tags=tags or [],
        applies_to=applies_to,
    )
    logger.info(f"remember | saved to {path}")
    return str(path)
