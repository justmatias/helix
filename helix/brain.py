from pathlib import Path

from helix.convention import Convention
from helix.settings import Settings


class Brain:
    @property
    def index(self) -> Path:
        return Settings.HELIX_INDEX

    @property
    def conventions(self) -> Path:
        return Settings.HELIX_CONVENTIONS

    @property
    def is_initialized(self) -> bool:
        return self.index.exists()

    @property
    def content(self) -> str:
        return self.index.read_text()

    @property
    def index_lines(self) -> list[str]:
        return self.content.splitlines(keepends=True)

    def initialize(self) -> None:
        self.conventions.mkdir(parents=True, exist_ok=True)
        if not self.is_initialized:
            self.index.write_text("# Helix Convention Index\n\n")

    def remember(
        self,
        *,
        name: str,
        body: str,
        tags: list[str],
        applies_to: list[str] | None = None,
    ) -> Path:
        convention = Convention(
            name=name, body=body, tags=tags, applies_to=applies_to or []
        )
        convention.file_path.write_text(convention.to_markdown())
        self._add_convention_to_index(convention)

        return convention.file_path

    def index_line_for(self, name: str) -> str | None:
        return next(
            (line for line in self.index_lines if line.startswith(f"- [{name}](")),
            None,
        )

    def convention_for(self, name: str) -> Convention | None:
        path = self.conventions / f"{name}.md"
        if not path.exists():
            return None
        try:
            return Convention.from_markdown(path.read_text())
        except ValueError:
            return None

    def _add_convention_to_index(self, convention: Convention) -> None:
        lines = [
            line
            for line in self.index_lines
            if not line.startswith(f"- [{convention.name}](")
        ]
        content = "".join(lines).rstrip("\n") + "\n"
        content += convention.index_line() + "\n"
        self.index.write_text(content)

    def list_conventions(self, tags: list[str] | None = None) -> list[str]:
        if not self.is_initialized:
            return []
        lines = [line for line in self.index_lines if line.startswith("- [")]
        if not tags:
            return lines

        return self._filter_index_lines_by_tags(lines, tags)

    @staticmethod
    def _filter_index_lines_by_tags(lines: list[str], tags: list[str]) -> list[str]:
        tags_set = set(tags)
        return [
            line for line in lines if Convention.tags_from_index_line(line) & tags_set
        ]

    def recall(self, query: str, tags: list[str] | None = None) -> list[str]:
        lines = [
            f"{path}:{line_number}:{line}"
            for path in self.conventions.glob("*.md")
            for line_number, line in enumerate(path.read_text().splitlines(), 1)
            if query.lower() in line.lower()
        ]

        if not tags:
            return lines

        tags_set = set(tags)
        allowed_names = {
            convention.name
            for convention in self._load_conventions()
            if tags_set & set(convention.tags)
        }
        return [line for line in lines if any(name in line for name in allowed_names)]

    def _load_conventions(self) -> list[Convention]:
        conventions = []
        for path in self.conventions.glob("*.md"):
            try:
                conventions.append(Convention.from_markdown(path.read_text()))
            except ValueError:
                pass
        return conventions

    def forget(self, name: str) -> bool:
        file_path = self.conventions / f"{name}.md"
        if not file_path.exists():
            return False
        file_path.unlink()
        existing_line = self.index_line_for(name)
        if existing_line:
            self.index.write_text(self.content.replace(existing_line, ""))
        return True
