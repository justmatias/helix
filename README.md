# Helix

Global convention memory for AI coding agents — persist your coding preferences once, surface them in every Claude Code, Cursor, or MCP-compatible session.

## The problem

You keep re-explaining the same conventions to every new agent session: _"prefer Pydantic v2", "always async I/O", "use Typer for CLIs"_. Helix fixes that. It's a lightweight store of verbatim convention notes that any agent can read via MCP.

## How it works

```
~/.dev_brain/
├── INDEX.md                    # one-line hook per convention (always-loaded)
├── conventions/
│   ├── python-async.md
│   ├── pydantic-validation.md
│   └── ...
└── projects/                   # optional per-project overrides
    └── <repo-name>/
        └── <override>.md
```

Each file has frontmatter:

```markdown
---
name: pydantic-validation
tags: [python, validation]
applies_to: [python]
---

Prefer Pydantic v2 for any external-boundary validation.
```

`INDEX.md` is a lightweight index — one line per convention, kept small so it's cheap to always load. Full bodies are pulled on demand.

## Install

```bash
pip install helix  # coming soon — for now, clone and use uv
git clone https://github.com/matiasgimenez/helix
cd helix
uv sync
```

## CLI usage

```bash
# Save a convention
helix remember --name pydantic-validation --tags python,validation \
  "Prefer Pydantic v2 for any external-boundary validation."

# List conventions (optionally filtered by tag)
helix list
helix list --tags python

# Search conventions
helix recall "validation"
helix recall "async" --tags python

# Remove a convention
helix forget pydantic-validation

# Start the MCP server
helix serve
```

## MCP server

`helix serve` exposes four tools to any MCP-compatible client:

| Tool                                      | Description                                     |
| ----------------------------------------- | ----------------------------------------------- |
| `remember(name, body, tags, applies_to?)` | Write a convention file and append to the index |
| `recall(query, tags?)`                    | Ripgrep across files, return matched snippets   |
| `list_conventions(tags?)`                 | Return the index, filtered by tag               |
| `forget(name)`                            | Remove a file and its index entry               |

### Claude Code setup

Add to your project's `CLAUDE.md`:

```markdown
On the first turn, call `list_conventions(tags=["python"])` to surface relevant global conventions.
```

Add to `~/.claude/claude_desktop_config.json` (or your client's MCP config):

```json
{
	"mcpServers": {
		"helix": {
			"command": "helix",
			"args": ["serve"]
		}
	}
}
```

## License

MIT
