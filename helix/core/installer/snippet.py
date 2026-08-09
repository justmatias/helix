import re

START_MARKER = "<!-- helix:start -->"
END_MARKER = "<!-- helix:end -->"

SNIPPET = (
    "## Helix — Global Conventions\n"
    "\n"
    "Use `recall` (MCP) or `helix recall <query>` (CLI) to load the full text of "
    "any convention that looks relevant, and `remember` to save a new one when I "
    "state a preference that should outlive this project.\n"
    "\n"
    "If the convention index was not already injected at session start, run "
    "`list_conventions` (MCP) or `helix list` to see it.\n"
)

BLOCK_PATTERN = re.compile(
    re.escape(START_MARKER) + r".*?" + re.escape(END_MARKER),
    re.DOTALL,
)
