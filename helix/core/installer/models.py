from pathlib import Path

from pydantic import BaseModel, ConfigDict, Field

from .scope import Scope
from .targets import InstallTarget, SnippetTarget

__all__ = ["Client", "Scope", "SnippetBlock"]


class Client(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)

    key: str = Field(description="Stable identifier for the client (e.g. 'claude').")
    name: str = Field(description="Human-readable client name shown in CLI prompts.")
    snippet: SnippetTarget = Field(
        description="The instruction-snippet target every client has."
    )
    extra_targets: list[InstallTarget] = Field(
        default_factory=list,
        description="Additional targets (MCP config, session hook) this client supports.",
    )
    detect_path: Path | None = Field(
        default=None,
        description=(
            "Directory checked to detect whether the client is installed. "
            "Defaults to snippet.global_path.parent when None."
        ),
    )

    @property
    def all_targets(self) -> list[InstallTarget]:
        return [self.snippet, *self.extra_targets]

    @property
    def installation_directory(self) -> Path:
        if self.detect_path is not None:
            return self.detect_path
        return self.snippet.global_path.parent

    def path_for(self, scope: Scope, project_root: Path) -> Path:
        return self.snippet.path_for(scope, project_root)


class SnippetBlock(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)

    client: Client = Field(description="The client whose config file holds the block.")
    scope: Scope = Field(
        description="Whether the block was found in global or project scope."
    )
    path: Path = Field(
        description="Resolved config file where the helix block was detected."
    )
