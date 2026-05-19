import re

START_MARKER = "<!-- helix:start -->"
END_MARKER = "<!-- helix:end -->"

SNIPPET = (
    "## Helix — Global Conventions\n"
    "\n"
    "If the `helix` CLI is available on PATH, run `helix list` at the start of "
    "every session and treat the output as global coding conventions that apply "
    "across projects. Use `helix recall <query>` to load the full text of any "
    "convention that looks relevant.\n"
)

BLOCK_PATTERN = re.compile(
    re.escape(START_MARKER) + r".*?" + re.escape(END_MARKER),
    re.DOTALL,
)
