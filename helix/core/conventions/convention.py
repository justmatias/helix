import re
from pathlib import Path
from typing import Self

import frontmatter
from pydantic import BaseModel, ConfigDict, Field

from helix.core.settings import Settings

CONVENTION_REGEX = r"\[([^\]]*)\] —"


class Convention(BaseModel):
    name: str
    body: str
    tags: list[str] = Field(default_factory=list)
    applies_to: list[str] = Field(default_factory=list)

    model_config = ConfigDict(extra="ignore")

    @property
    def file_path(self) -> Path:
        return Settings.HELIX_CONVENTIONS / f"{self.name}.md"

    def to_markdown(self) -> str:
        post = frontmatter.Post(
            self.body,
            name=self.name,
            tags=self.tags,
            applies_to=self.applies_to,
        )
        return str(frontmatter.dumps(post)) + "\n"

    @classmethod
    def from_markdown(cls, text: str) -> Self:
        post = frontmatter.loads(text)
        if not post.metadata.get("name"):
            raise ValueError("Invalid convention file: missing 'name' field")
        return cls.model_validate({"body": post.content, **post.metadata})

    def index_line(self) -> str:
        first_line = self.body.strip().splitlines()[0] if self.body.strip() else ""
        if len(first_line) > 80:
            first_line = first_line[:77] + "..."
        tags_string = ",".join(self.tags)
        return f"- [{self.name}](conventions/{self.name}.md) [{tags_string}] — {first_line}"

    @staticmethod
    def tags_from_index_line(line: str) -> set[str]:
        match = re.search(CONVENTION_REGEX, line)
        if not match:
            return set()
        return {tag.strip() for tag in match.group(1).split(",") if tag.strip()}
