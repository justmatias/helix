import re

START_MARKER = "<!-- helix:start -->"
END_MARKER = "<!-- helix:end -->"

SNIPPET = (
    "## Helix — Global Conventions\n"
    "\n"
    "On the first turn, call the `list_conventions` MCP tool with this project's "
    "stack tags (e.g. `list_conventions(tags=[\"python\"])`) to surface relevant "
    "global coding conventions. If the Helix MCP server is not connected, run "
    "`helix list` instead.\n"
    "\n"
    "Use `recall` (MCP) or `helix recall <query>` (CLI) to load the full text of "
    "any convention that looks relevant.\n"
)

BLOCK_PATTERN = re.compile(
    re.escape(START_MARKER) + r".*?" + re.escape(END_MARKER),
    re.DOTALL,
)
