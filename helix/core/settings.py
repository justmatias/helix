from pathlib import Path

from pydantic import Field
from pydantic_settings import BaseSettings


class AppSettings(BaseSettings):
    HOME_DIRECTORY: Path = Field(default=Path.home())
    HELIX_REQUIRE_CONFIRM: bool = Field(default=False)
    HELIX_BRAIN_DIR: Path | None = Field(
        default=None,
        description="Override for the brain location (e.g. a synced dotfiles repo).",
    )

    @property
    def HELIX_BRAIN(self) -> Path:
        return self.HELIX_BRAIN_DIR or self.HOME_DIRECTORY / ".dev_brain"

    @property
    def HELIX_CONVENTIONS(self) -> Path:
        return self.HELIX_BRAIN / "conventions"

    @property
    def HELIX_INDEX(self) -> Path:
        return self.HELIX_BRAIN / "INDEX.md"


Settings = AppSettings()
