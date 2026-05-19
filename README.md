# Helix

Global convention memory for AI coding agents — persist your coding preferences once, surface them in every Claude Code, Cursor, or MCP-compatible session.

## Install

```bash
# With uv (recommended)
uv tool install helix-memory

# Or with pip
pip install helix-memory
```

## Quick start

```bash
# 1. Hook Helix into your agent (Claude Code, Cursor, …).
helix install

# 2. Save your first convention.
helix remember pydantic-validation \
  "Prefer Pydantic v2 for any external-boundary validation." \
  --tags python,validation
```

From there, your next agent session will see the conventions automatically.

## CLI

```bash
helix remember <name> "<body>" --tags <comma,separated>
helix list [--tags <tag>]
helix recall "<query>" [--tags <tag>]
helix forget <name>
helix install   # wire Helix into your agent
helix uninstall # remove the integration
helix serve     # start the MCP server
```

## MCP server

`helix serve` exposes four tools to any MCP-compatible client: `remember`, `recall`, `list_conventions`, `forget`.

Add to your client's MCP config (e.g. `~/.claude/claude_desktop_config.json`):

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
