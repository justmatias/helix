import re
from dataclasses import dataclass, field
from pathlib import Path

import frontmatter

from helix.settings import Settings

CONVENTION_REGEX = r"\[([^\]]*)\] —"


@dataclass
class Convention:
    name: str
    body: str
    tags: list[str] = field(default_factory=list)
    applies_to: list[str] = field(default_factory=list)

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
        return frontmatter.dumps(post) + "\n"

    @classmethod
    def from_markdown(cls, text: str) -> "Convention":
        post = frontmatter.loads(text)
        name = post.get("name", "")
        if not name:
            raise ValueError("Invalid convention file: missing 'name' field")
        return cls(
            name=name,
            body=post.content,
            tags=list(post.get("tags", [])),
            applies_to=list(post.get("applies_to", [])),
        )

    def index_line(self) -> str:
        first_line = self.body.strip().splitlines()[0] if self.body.strip() else ""
        if len(first_line) > 80:
            first_line = first_line[:77] + "..."
        tags_string = ",".join(self.tags)
        return (
            f"- [{self.name}](conventions/{self.name}.md) [{tags_string}] — {first_line}"
        )

    @staticmethod
    def tags_from_index_line(line: str) -> set[str]:
        match = re.search(CONVENTION_REGEX, line)
        if not match:
            return set()
        return {tag.strip() for tag in match.group(1).split(",") if tag.strip()}
