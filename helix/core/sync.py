import os
import subprocess
from dataclasses import dataclass, field
from enum import StrEnum
from pathlib import Path

from .conventions import Brain
from .settings import Settings

SYNC_BRANCH = "main"
NOT_CONFIGURED_MESSAGE = (
    "Brain is not set up for sync. Run `helix sync init <remote-url>` first."
)

COMMIT_METADATA = {
    "GIT_AUTHOR_NAME": "helix",
    "GIT_AUTHOR_EMAIL": "helix@localhost",
    "GIT_COMMITTER_NAME": "helix",
    "GIT_COMMITTER_EMAIL": "helix@localhost",
}


class SyncError(RuntimeError):
    """Raised when a git operation backing sync/backup fails."""


class MergeStrategy(StrEnum):
    KEEP_LOCAL = "keep-local"
    OVERWRITE = "overwrite"
    RENAME_CONFLICT = "rename-conflict"


@dataclass
class MergeResult:
    added: list[str] = field(default_factory=list)
    overwritten: list[str] = field(default_factory=list)
    renamed: list[str] = field(default_factory=list)
    kept_local: list[str] = field(default_factory=list)

    def summary(self) -> str:
        parts = [
            f"{len(names)} {label}" + (f": {', '.join(names)}" if names else "")
            for label, names in (
                ("added", self.added),
                ("overwritten", self.overwritten),
                ("renamed (conflict)", self.renamed),
                ("kept local (conflict)", self.kept_local),
            )
            if names
        ]
        return "; ".join(parts) if parts else "already up to date"


def run_git(
    *args: str,
    cwd: Path,
    check: bool = True,
    env: dict[str, str] | None = None,
) -> subprocess.CompletedProcess[str]:
    full_env = {**os.environ, **env} if env else None
    result = subprocess.run(
        ["git", *args],
        cwd=cwd,
        check=False,
        capture_output=True,
        text=True,
        env=full_env,
    )
    if check and result.returncode != 0:
        raise SyncError(result.stderr.strip() or f"git {' '.join(args)} failed")
    return result


def sync_init(remote_url: str) -> None:
    """Make the brain directory a git repo (if needed) and point origin at ``remote_url``."""
    Brain().initialize()
    is_configured = (Settings.HELIX_BRAIN / ".git").exists()
    if not is_configured:
        run_git("init", "-b", SYNC_BRANCH, cwd=Settings.HELIX_BRAIN)

    remotes = run_git("remote", cwd=Settings.HELIX_BRAIN).stdout.split()
    if "origin" in remotes:
        run_git("remote", "set-url", "origin", remote_url, cwd=Settings.HELIX_BRAIN)
    else:
        run_git("remote", "add", "origin", remote_url, cwd=Settings.HELIX_BRAIN)


def sync_push(message: str = "Update conventions") -> None:
    """Commit any local changes and push them to origin."""
    is_configured = (Settings.HELIX_BRAIN / ".git").exists()
    if not is_configured:
        raise SyncError(NOT_CONFIGURED_MESSAGE)

    run_git("add", "-A", cwd=Settings.HELIX_BRAIN)
    status = run_git("status", "--porcelain", cwd=Settings.HELIX_BRAIN).stdout
    if status.strip():
        run_git("commit", "-m", message, cwd=Settings.HELIX_BRAIN, env=COMMIT_METADATA)
    elif run_git(
        "rev-parse", "--verify", "-q", "HEAD", cwd=Settings.HELIX_BRAIN, check=False
    ).returncode:
        raise SyncError("Nothing to push yet — save a convention first.")

    run_git(
        "push",
        "-u",
        "origin",
        f"HEAD:refs/heads/{SYNC_BRANCH}",
        cwd=Settings.HELIX_BRAIN,
    )


def sync_pull(strategy: MergeStrategy = MergeStrategy.KEEP_LOCAL) -> MergeResult:
    """Fetch origin and merge its conventions into the local brain per ``strategy``."""
    is_configured = (Settings.HELIX_BRAIN / ".git").exists()
    if not is_configured:
        raise SyncError(NOT_CONFIGURED_MESSAGE)

    brain = Brain()
    brain.initialize()

    fetch = run_git(
        "fetch", "origin", SYNC_BRANCH, cwd=Settings.HELIX_BRAIN, check=False
    )
    if fetch.returncode:
        if "couldn't find remote ref" in fetch.stderr:
            return MergeResult()
        raise SyncError(fetch.stderr.strip() or "git fetch failed")

    result = _merge_from_fetch_head(brain, strategy)

    run_git("add", "-A", cwd=Settings.HELIX_BRAIN)
    status = run_git("status", "--porcelain", cwd=Settings.HELIX_BRAIN).stdout
    if not status.strip():
        return result

    tree = run_git("write-tree", cwd=Settings.HELIX_BRAIN).stdout.strip()
    head = run_git(
        "rev-parse", "--verify", "-q", "HEAD", cwd=Settings.HELIX_BRAIN, check=False
    )
    parents = ["-p", head.stdout.strip()] if head.returncode == 0 else []
    parents += ["-p", "FETCH_HEAD"]

    commit = run_git(
        "commit-tree",
        tree,
        *parents,
        "-m",
        "Merge conventions from origin",
        cwd=Settings.HELIX_BRAIN,
        env=COMMIT_METADATA,
    ).stdout.strip()
    run_git("update-ref", "HEAD", commit, cwd=Settings.HELIX_BRAIN)

    return result


def sync_clone(
    remote_url: str, strategy: MergeStrategy = MergeStrategy.KEEP_LOCAL
) -> MergeResult:
    """Configure origin as ``remote_url`` and pull, merging into any existing local conventions."""
    sync_init(remote_url)
    return sync_pull(strategy)


def get_remote_convention_paths(brain_dir: Path) -> list[str]:
    result = run_git(
        "ls-tree",
        "--name-only",
        "-r",
        "FETCH_HEAD",
        "--",
        "conventions",
        cwd=brain_dir,
        check=False,
    )
    if result.returncode:
        return []
    return sorted(path for path in result.stdout.splitlines() if path.endswith(".md"))


def _merge_from_fetch_head(brain: Brain, strategy: MergeStrategy) -> MergeResult:
    brain_dir = Settings.HELIX_BRAIN
    brain.conventions.mkdir(parents=True, exist_ok=True)
    result = MergeResult()

    for path in get_remote_convention_paths(brain_dir):
        name = Path(path).name
        remote_content = run_git("show", f"FETCH_HEAD:{path}", cwd=brain_dir).stdout
        local_file = brain.conventions / name

        if not local_file.exists():
            local_file.write_text(remote_content)
            result.added.append(name)
        elif local_file.read_text() == remote_content:
            continue
        elif strategy is MergeStrategy.OVERWRITE:
            local_file.write_text(remote_content)
            result.overwritten.append(name)
        elif strategy is MergeStrategy.RENAME_CONFLICT:
            new_name = brain.free_name(f"{Path(name).stem}-remote")
            (brain.conventions / f"{new_name}.md").write_text(remote_content)
            result.renamed.append(f"{new_name}.md")
        else:
            result.kept_local.append(name)

    brain.rebuild_index()
    return result
