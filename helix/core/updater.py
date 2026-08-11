import shutil
import subprocess
import sys

PACKAGE_NAME = "helix-memory"


def _installed_via_uv_tool() -> bool:
    """Whether ``uv tool list`` reports helix-memory as one of its managed tools."""
    if not shutil.which("uv"):
        return False
    result = subprocess.run(
        ["uv", "tool", "list"], check=False, capture_output=True, text=True
    )
    installed = {line.split()[0] for line in result.stdout.splitlines() if line.strip()}
    return PACKAGE_NAME in installed


def update_command() -> list[str]:
    """The command that upgrades the installed helix-memory package in place."""
    if _installed_via_uv_tool():
        return ["uv", "tool", "upgrade", PACKAGE_NAME]
    return [sys.executable, "-m", "pip", "install", "--upgrade", PACKAGE_NAME]


def update() -> subprocess.CompletedProcess[bytes]:
    """Run the resolved update command in place, returning the completed process."""
    return subprocess.run(update_command(), check=False)
