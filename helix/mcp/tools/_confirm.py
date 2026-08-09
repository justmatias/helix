from collections.abc import Callable

from helix.core.settings import Settings


def confirm_gate(
    confirm: bool,
    preview: Callable[[], str | None],
    action: Callable[[], str],
) -> str:
    """Run ``action``, unless confirmation is required and not yet given.

    When ``Settings.HELIX_REQUIRE_CONFIRM`` is set and ``confirm`` is False,
    ``preview`` decides what happens: returning text asks for confirmation
    and shows that text as-is; returning ``None`` means there's nothing to
    preview (e.g. the target doesn't exist), so ``action`` runs anyway and
    reports that.
    """
    if not Settings.HELIX_REQUIRE_CONFIRM or confirm:
        return action()

    text = preview()
    return action() if text is None else text
