from helix.core import Brain, Convention
from helix.utils import logger

from ._confirm import confirm_gate


def remember(
    name: str,
    body: str,
    tags: list[str] | None = None,
    confirm: bool = False,
) -> str:
    logger.info(f"remember | name={name} tags={tags}")

    def _preview() -> str:
        preview_convention = Convention(name=name, body=body, tags=tags or [])
        logger.info(f"remember | preview only (confirm=False) for {name!r}")
        return (
            "Confirmation required. Re-call `remember` with the same arguments and "
            "`confirm=True` to write.\n\n"
            f"Target path: {preview_convention.file_path}\n\n"
            "--- file contents ---\n"
            f"{preview_convention.to_markdown()}"
        )

    def _action() -> str:
        path = Brain().remember(name=name, body=body, tags=tags or [])
        logger.info(f"remember | saved to {path}")
        return str(path)

    return confirm_gate(confirm, _preview, _action)
