"""SessionStart hook wiring, so the convention index loads without the agent asking.

Claude Code injects a SessionStart hook's stdout into the session context, which
makes it a stronger guarantee than the instruction snippet in ``snippet.py``.
"""

import json
from pathlib import Path

from .models import Client, Scope

HOOK_EVENT = "SessionStart"
HOOK_COMMAND = "helix list"
HOOK_ENTRY = {
    "matcher": "startup|resume|clear",
    "hooks": [{"type": "command", "command": HOOK_COMMAND}],
}


def install_hook(client: Client, scope: Scope, project_root: Path) -> Path | None:
    """Add the Helix SessionStart hook to the client's settings file.

    Returns the path written, ``None`` if this client has no hook settings for
    the requested scope or the hook is already present.
    """
    path = client.hook_path_for(scope, project_root)
    if not path:
        return None

    data: dict = json.loads(path.read_text()) if path.exists() else {}
    entries: list[dict] = data.setdefault("hooks", {}).setdefault(HOOK_EVENT, [])
    if any(
        hook.get("command") == HOOK_COMMAND
        for entry in entries
        for hook in entry.get("hooks", []) or []
    ):
        return None

    entries.append(HOOK_ENTRY)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2) + "\n")
    return path


def uninstall_hook(client: Client, scope: Scope, project_root: Path) -> bool:
    """Remove the Helix SessionStart hook. Returns ``True`` if one was removed."""
    path = client.hook_path_for(scope, project_root)
    if path is None or not path.exists():
        return False

    data: dict = json.loads(path.read_text() or "{}")
    entries = data.get("hooks", {}).get(HOOK_EVENT, [])
    remaining = [
        entry
        for entry in entries
        if not any(
            hook.get("command") == HOOK_COMMAND for hook in entry.get("hooks", []) or []
        )
    ]
    if len(remaining) == len(entries):
        return False

    data["hooks"][HOOK_EVENT] = remaining
    hooks = data.get("hooks", {})
    if not hooks.get(HOOK_EVENT):
        hooks.pop(HOOK_EVENT, None)
    if not hooks:
        data.pop("hooks", None)

    if data:
        path.write_text(json.dumps(data, indent=2) + "\n")
    else:
        path.unlink()
    return True
