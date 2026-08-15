# Helix

[![PyPI](https://img.shields.io/pypi/v/helix-memory)](https://pypi.org/project/helix-memory/)
[![CI](https://github.com/justmatias/helix/actions/workflows/ci.yml/badge.svg)](https://github.com/justmatias/helix/actions/workflows/ci.yml)
[![Python](https://img.shields.io/pypi/pyversions/helix-memory)](https://pypi.org/project/helix-memory/)
[![License: MIT](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)

Global convention memory for AI coding agents — persist your coding preferences once, surface them in every Claude Code, Cursor, Codex, Opencode, or other MCP-compatible session.

## Install

```bash
# With uv (recommended)
uv tool install helix-memory

# Or with pip
pip install helix-memory
```

Later, run `helix update` to upgrade to the latest version — it re-runs
whichever of the two put it there.

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
helix version   # print the installed version
helix update    # upgrade the installed helix-memory package

helix sync init <remote-url>                          # configure a git remote for backup
helix sync push [--message <msg>]                      # commit and push local conventions
helix sync pull [--strategy keep-local|overwrite|rename-conflict]   # merge in remote changes
helix sync clone <remote-url> [--strategy ...]          # restore/merge conventions on a new host
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

### Sync

For a first-class backup instead, point Helix at a dedicated git repository
(GitHub, GitLab, a private host — anything `git push`/`git fetch` can reach)
and it will manage the brain directory as a git repo for you:

```bash
# On your first machine
helix sync init git@github.com:you/helix-brain.git
helix sync push

# On any other machine
helix sync clone git@github.com:you/helix-brain.git

# Later, on either machine
helix sync push   # back up local changes
helix sync pull   # bring in changes made elsewhere
```

`push` commits and pushes anything new; `pull`/`clone` fetch the remote and
merge it into whatever conventions already exist locally, then regenerate
`INDEX.md` from the merged result. Conventions that only exist on one side are
kept automatically. When the same convention name has diverged on both sides,
`--strategy` controls what happens:

- `keep-local` (default) — leave the local file untouched.
- `overwrite` — replace the local file with the remote version.
- `rename-conflict` — keep the local file and save the remote version
  alongside it as `<name>-remote.md`, so nothing is lost.

Sync uses your existing git/SSH credentials (or `gh`'s), so it works with
whatever authentication you already have configured for the remote.

## MCP server

`helix serve` starts a stdio MCP server that exposes four tools: `remember`, `recall`, `list_conventions`, `forget`.

`helix install` wires this up automatically for a supported client: it writes an
instructions snippet to the client's rules file (`CLAUDE.md`, `AGENTS.md`, or
`.cursor/rules/helix.mdc`), registers the MCP server, and — for Claude Code —
adds a `SessionStart` hook. Supported clients: **Claude Code**, **Cursor**,
**Codex CLI**, and **Opencode**. The sections below show the config `helix
install` writes, for setting it up by hand.

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

### Codex CLI

Codex only supports a global MCP config, in TOML:

```toml
# ~/.codex/config.toml
[mcp_servers.helix]
command = "helix"
args = ["serve"]
```

### Opencode

**Global**:

```json
// ~/.config/opencode/opencode.json
{
  "mcp": {
    "helix": {
      "type": "local",
      "command": ["helix", "serve"],
      "enabled": true
    }
  }
}
```

**Project-scoped**:

```json
// opencode.json at the project root
{
  "mcp": {
    "helix": {
      "type": "local",
      "command": ["helix", "serve"],
      "enabled": true
    }
  }
}
```

After adding the config, restart your client. Verify the server is visible: in Claude Code run `/mcp`, in Cursor open the MCP panel.

## License

MIT
