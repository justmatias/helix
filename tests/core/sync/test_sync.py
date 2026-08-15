import subprocess
from collections.abc import Callable
from pathlib import Path

import pytest

from helix.core import (
    Brain,
    MergeStrategy,
    Settings,
    SyncError,
    sync_clone,
    sync_init,
    sync_pull,
    sync_push,
)


def test_sync_init_creates_git_repo(remote_repository: str) -> None:
    sync_init(remote_repository)
    assert (Settings.HELIX_BRAIN / ".git").is_dir()


def test_sync_init_configures_origin_remote(remote_repository: str) -> None:
    sync_init(remote_repository)
    result = subprocess.run(
        ["git", "remote", "get-url", "origin"],
        cwd=Settings.HELIX_BRAIN,
        check=True,
        capture_output=True,
        text=True,
    )
    assert result.stdout.strip() == remote_repository


def test_sync_init_is_idempotent_and_updates_url(
    remote_repository: str, tmp_path: Path
) -> None:
    other_remote = tmp_path / "other.git"
    subprocess.run(["git", "init", "--bare", "-q", str(other_remote)], check=True)

    sync_init(remote_repository)
    sync_init(str(other_remote))

    result = subprocess.run(
        ["git", "remote", "get-url", "origin"],
        cwd=Settings.HELIX_BRAIN,
        check=True,
        capture_output=True,
        text=True,
    )
    assert result.stdout.strip() == str(other_remote)


def test_sync_push_requires_init() -> None:
    with pytest.raises(SyncError):
        sync_push()


def test_sync_push_requires_something_to_push() -> None:
    """A bare, un-initialized brain has no HEAD and nothing staged: pushing it is an error."""
    brain_dir = Settings.HELIX_BRAIN
    brain_dir.mkdir(parents=True, exist_ok=True)
    subprocess.run(["git", "init", "-q", "-b", "main", str(brain_dir)], check=True)
    with pytest.raises(SyncError):
        sync_push()


@pytest.mark.usefixtures("_remember_convention")
def test_sync_push_uploads_conventions(
    remote_repository: str, remote_files: Callable[[], list[str]]
) -> None:
    sync_init(remote_repository)
    sync_push()
    assert remote_files() == ["conv-a.md"]


def test_sync_pull_requires_init() -> None:
    with pytest.raises(SyncError):
        sync_pull()


def test_sync_pull_against_empty_remote_is_a_noop(remote_repository: str) -> None:
    sync_init(remote_repository)
    result = sync_pull()
    assert result.summary() == "already up to date"


def test_sync_pull_raises_on_unreachable_remote(tmp_path: Path) -> None:
    sync_init(str(tmp_path / "does-not-exist.git"))
    with pytest.raises(SyncError):
        sync_pull()


def test_sync_pull_is_a_noop_when_remote_has_no_conventions_dir(
    remote_repository: str, brain: Brain
) -> None:
    other_clone = brain.conventions.parent.parent / "unrelated-clone"
    subprocess.run(
        ["git", "clone", "-q", remote_repository, str(other_clone)], check=True
    )
    (other_clone / "README.md").write_text("Not a helix brain.\n")
    subprocess.run(["git", "add", "-A"], cwd=other_clone, check=True)
    subprocess.run(
        ["git", "-c", "user.name=x", "-c", "user.email=x@x", "commit", "-m", "seed"],
        cwd=other_clone,
        check=True,
    )
    subprocess.run(
        ["git", "push", "origin", "HEAD:refs/heads/main"], cwd=other_clone, check=True
    )

    sync_init(remote_repository)
    result = sync_pull()
    assert result.summary() == "already up to date"


@pytest.mark.usefixtures("_remember_convention")
def test_sync_push_raises_on_diverged_unrelated_history(
    remote_repository: str, tmp_path: Path
) -> None:
    sync_init(remote_repository)
    sync_push()

    Settings.HOME_DIRECTORY = tmp_path / "other-host"
    other_brain = Brain()
    other_brain.initialize()
    other_brain.remember(name="conv-b", body="Body B.", tags=["typescript"])
    sync_init(
        remote_repository
    )  # init only: no fetch/merge, so this host's history is unrelated
    with pytest.raises(SyncError):
        sync_push()


@pytest.mark.usefixtures("_remember_convention")
def test_sync_clone_restores_conventions_on_a_fresh_host(
    remote_repository: str, tmp_path: Path
) -> None:
    sync_init(remote_repository)
    sync_push()

    Settings.HOME_DIRECTORY = tmp_path / "other-host"
    fresh_brain = Brain()
    assert not fresh_brain.is_initialized

    result = sync_clone(remote_repository)

    assert result.added == ["conv-a.md"]
    assert (fresh_brain.conventions / "conv-a.md").exists()
    assert "conv-a" in fresh_brain.content

    second_pull = sync_pull()
    assert second_pull.summary() == "already up to date"


@pytest.mark.usefixtures("_remember_convention")
def test_sync_pull_reconciles_conflicting_convention_per_strategy(
    remote_repository: str, brain: Brain, tmp_path: Path
) -> None:
    brain.remember(name="shared", body="Local version.", tags=["python"])
    sync_init(remote_repository)
    sync_push()

    # A second host pushes a divergent edit of the same convention.
    Settings.HOME_DIRECTORY = tmp_path / "other-host"
    other_brain = Brain()
    sync_clone(remote_repository)
    other_brain.remember(name="shared", body="Remote version.", tags=["python"])
    sync_push()

    # Back on the first host, `shared` now conflicts with what's on origin.
    Settings.HOME_DIRECTORY = tmp_path
    keep_local_result = sync_pull(strategy=MergeStrategy.KEEP_LOCAL)
    assert keep_local_result.kept_local == ["shared.md"]
    assert "Local version." in (brain.conventions / "shared.md").read_text()

    overwrite_result = sync_pull(strategy=MergeStrategy.OVERWRITE)
    assert overwrite_result.overwritten == ["shared.md"]
    assert "Remote version." in (brain.conventions / "shared.md").read_text()

    # Diverge again locally so rename-conflict has something to reconcile.
    brain.remember(name="shared", body="Local version again.", tags=["python"])
    rename_result = sync_pull(strategy=MergeStrategy.RENAME_CONFLICT)
    assert rename_result.renamed == ["shared-remote.md"]
    assert (brain.conventions / "shared-remote.md").exists()
    assert "Remote version." in (brain.conventions / "shared-remote.md").read_text()
    assert "Local version again." in (brain.conventions / "shared.md").read_text()


@pytest.mark.usefixtures("_remember_convention")
def test_sync_pull_rebuilds_index(
    remote_repository: str, brain: Brain, tmp_path: Path
) -> None:
    sync_init(remote_repository)
    sync_push()

    Settings.HOME_DIRECTORY = tmp_path / "other-host"
    other_brain = Brain()
    sync_clone(remote_repository)
    other_brain.remember(name="conv-b", body="Body B.", tags=["typescript"])
    sync_push()

    Settings.HOME_DIRECTORY = tmp_path
    sync_pull()
    assert "conv-a" in brain.content
    assert "conv-b" in brain.content


@pytest.mark.usefixtures("_remember_convention")
def test_sync_push_after_pull_merge_is_a_fast_forward(
    remote_repository: str, remote_files: Callable[[], list[str]], tmp_path: Path
) -> None:
    sync_init(remote_repository)
    sync_push()

    Settings.HOME_DIRECTORY = tmp_path / "other-host"
    other_brain = Brain()
    sync_clone(remote_repository)
    other_brain.remember(name="conv-b", body="Body B.", tags=["typescript"])
    sync_push()

    Settings.HOME_DIRECTORY = tmp_path
    sync_pull()
    # The merge commit has origin as a parent, so this push is a fast-forward and won't raise.
    sync_push()
    assert remote_files() == ["conv-a.md", "conv-b.md"]
