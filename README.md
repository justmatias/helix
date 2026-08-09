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

# 2. Save your first convention. The name is derived from the body.
helix remember "Prefer Pydantic v2 for any external-boundary validation." -t python
```

From there, your next agent session will see the conventions automatically.

## CLI

```bash
helix remember "<body>" [--name <name>] [--tags <comma,separated>]
helix list [--tags <tag>]
helix recall "<query>" [--tags <tag>]
helix edit <name>     # open the convention in $EDITOR
helix forget <name>
helix install   [--client <key>] [--scope global|project] [--yes]
helix uninstall [--yes]
helix serve     # start the MCP server
```

`remember` takes the body three ways — as an argument, from stdin, or from `$EDITOR`:

```bash
helix remember "Always use async I/O." -t python
git log --format=%s -1 | helix remember -
helix remember                 # opens $EDITOR
```

The convention name is slugified from the body (`always-use-async-i-o`), with a
numeric suffix on collision. Pass `--name` to choose it yourself; an explicit
name overwrites any existing convention with that name.

`install` is scriptable, so it can live in a dotfiles bootstrap:

```bash
helix install --client claude --scope global --yes
```

## Storage

Conventions live in `~/.dev_brain/` as plain markdown, one file per convention,
plus an `INDEX.md`. Point `HELIX_BRAIN_DIR` at a directory you already sync to
carry them between machines:

```bash
export HELIX_BRAIN_DIR=~/dotfiles/brain
```

## MCP server

`helix serve` starts a stdio MCP server that exposes four tools: `remember`, `recall`, `list_conventions`, `forget`.

### Claude Code

`helix install` also writes a `SessionStart` hook, so the convention index is
injected into every session without the agent having to ask for it:

```json
// ~/.claude/settings.json (global) or .claude/settings.json (project)
{
  "hooks": {
    "SessionStart": [
      {
        "matcher": "startup|resume|clear",
        "hooks": [{ "type": "command", "command": "helix list" }]
      }
    ]
  }
}
```

Restart Claude Code after installing for the hook to take effect.

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
