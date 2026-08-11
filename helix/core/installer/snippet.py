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
    "Helix is the shared store across all my projects. Before saving anything to "
    "your own memory, check whether it's actually a general coding pattern, "
    "standard, or rule rather than a fact specific to this project — even if I "
    "only brought it up in this project's context. If so, save it here via "
    "`remember` instead, generalized and stripped of this project's specifics. "
    "Keep only genuinely project-specific facts in your own memory.\n"
    "\n"
    "If the convention index was not already injected at session start, run "
    "`list_conventions` (MCP) or `helix list` to see it.\n"
)

BLOCK_PATTERN = re.compile(
    re.escape(START_MARKER) + r".*?" + re.escape(END_MARKER),
    re.DOTALL,
)
