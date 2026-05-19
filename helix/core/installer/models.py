from enum import StrEnum
from pathlib import Path

from pydantic import BaseModel, Field


class Scope(StrEnum):
    GLOBAL = "global"
    PROJECT = "project"


class Client(BaseModel):
    key: str = Field(description="Stable identifier for the client (e.g. 'claude').")
    name: str = Field(description="Human-readable client name shown in CLI prompts.")
    global_path: Path = Field(
        description="Absolute path to the client's per-user (global) config file."
    )
    project_relative_path: Path = Field(
        description="Config file path relative to a project root, for project scope."
    )
    preamble: str | None = Field(
        default=None,
        description="Content prepended when creating a new config file (e.g. frontmatter).",
    )
    detect_path: Path | None = Field(
        default=None,
        description=(
            "Directory checked to detect whether the client is installed. "
            "Defaults to global_path.parent when None."
        ),
    )

    @property
    def installation_directory(self) -> Path:
        return self.detect_path if self.detect_path is not None else self.global_path.parent

    def path_for(self, scope: Scope, project_root: Path) -> Path:
        if scope == Scope.GLOBAL:
            return self.global_path
        return project_root / self.project_relative_path


class SnippetBlock(BaseModel):
    client: Client = Field(description="The client whose config file holds the block.")
    scope: Scope = Field(
        description="Whether the block was found in global or project scope."
    )
    path: Path = Field(
        description="Resolved config file where the helix block was detected."
    )
