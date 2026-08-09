import re


def parse_csv(value: str | None) -> list[str]:
    if not value:
        return []
    return [item.strip() for item in value.split(",")]


def slugify(text: str, max_words: int = 6) -> str:
    """Turn free-form text into a kebab-case convention name."""
    words = re.sub(r"[^a-z0-9]+", " ", text.lower()).split()
    return "-".join(words[:max_words])
