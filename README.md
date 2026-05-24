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

`helix serve` starts a stdio MCP server that exposes four tools: `remember`, `recall`, `list_conventions`, `forget`.

### Claude Code

**Project-scoped** (recommended — one `.mcp.json` per repo):

```json
// .mcp.json at the project root
{
  "mcpServers": {
    "helix": {
      "command": "helix",
      "args": ["serve"]
    }
  }
}
```

**User-scoped** (available in every project):

```bash
claude mcp add helix -- helix serve
```

Or edit `~/.claude.json` manually:

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

### Cursor

**Global** (all projects):

```json
// ~/.cursor/mcp.json
{
  "mcpServers": {
    "helix": {
      "command": "helix",
      "args": ["serve"]
    }
  }
}
```

**Project-scoped**:

```json
// .cursor/mcp.json at the project root
{
  "mcpServers": {
    "helix": {
      "command": "helix",
      "args": ["serve"]
    }
  }
}
```

After adding the config, restart your client. Verify the server is visible: in Claude Code run `/mcp`, in Cursor open the MCP panel.

## License

MIT
