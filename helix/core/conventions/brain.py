from pathlib import Path

from helix.core.settings import Settings

from .convention import Convention

INDEX_HEADER = "# Helix Convention Index\n\n"


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
            self.index.write_text(INDEX_HEADER)

    def rebuild_index(self) -> None:
        """Regenerate INDEX.md from every convention file currently on disk."""
        self.conventions.mkdir(parents=True, exist_ok=True)
        content = INDEX_HEADER + "".join(
            convention.index_line() + "\n" for convention in self._load_conventions()
        )
        self.index.write_text(content)

    def remember(self, *, name: str, body: str, tags: list[str]) -> Path:
        convention = Convention(name=name, body=body, tags=tags)
        convention.file_path.write_text(convention.to_markdown())
        self._add_convention_to_index(convention)

        return convention.file_path

    def free_name(self, name: str) -> str:
        """Return ``name``, or ``name-2``, ``name-3``… if it is already taken."""
        name = name or "convention"
        if not (self.conventions / f"{name}.md").exists():
            return name
        suffix = 2
        while (self.conventions / f"{name}-{suffix}.md").exists():
            suffix += 1
        return f"{name}-{suffix}"

    def reindex(self, name: str) -> bool:
        """Refresh the index line for a convention edited on disk."""
        convention = self.convention_for(name)
        if convention is None:
            return False
        self._add_convention_to_index(convention)
        return True

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

    def recall(self, query: str, tags: list[str] | None = None) -> list[Convention]:
        """Return every convention whose name, body, or tags match ``query``."""
        needle = query.lower()
        tags_set = set(tags or [])
        return [
            convention
            for convention in self._load_conventions()
            if self._matches(convention, needle, tags_set)
        ]

    @staticmethod
    def _matches(convention: Convention, needle: str, tags_set: set[str]) -> bool:
        haystack = " ".join([convention.name, convention.body, *convention.tags])
        return bool(
            needle in haystack.lower()
            and (not tags_set or tags_set & set(convention.tags))
        )

    def _load_conventions(self) -> list[Convention]:
        conventions = []
        for path in sorted(self.conventions.glob("*.md")):
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
