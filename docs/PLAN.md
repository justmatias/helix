# Implementation Plan

### Project Helix — A Global Convention Memory for AI Coding Agents

A lightweight, multi-client memory layer that persists **cross-project coding conventions** so you stop re-explaining the same preferences to every new agent session.

---

## 🎯 Problem & Scope

**The pain:** Re-explaining the same coding conventions ("prefer Pydantic", "always async I/O", "use Typer for CLIs") across different projects and different agents (Claude Code, Cursor, others).

**Out of scope** (handled elsewhere or not worth building):

- Project-specific context → already covered by `CLAUDE.md` + Claude Code's built-in per-project auto-memory.
- Repo onboarding (topology, dep audit, commit mining) → different problem.
- Semantic RAG over large doc corpora → unnecessary at this scale.

**In scope:** A small, global, multi-client-readable store of _verbatim_ convention notes, writable from chat via a "remember this" command.

---

## 🧱 Storage Layout

Plain markdown, no database. One convention per file.

```
~/.dev_brain/
├── INDEX.md                    # one-line hook per convention (loaded ~always)
├── conventions/
│   ├── python-async.md
│   ├── pydantic-validation.md
│   └── ...
└── projects/                   # optional per-project overrides
    └── <repo-name>/
        └── <override>.md
```

**File frontmatter:**

```markdown
---
name: pydantic-validation
tags: [python, validation]
applies_to: [python]
---

Prefer Pydantic v2 for any external-boundary validation. Reason: ...
```

**`INDEX.md`** is an index, not a memory — one line per file, kept under ~150 lines so it stays cheap to always-load.

**Override rule:** a file in `projects/<repo>/` with the same `name:` as a global file shadows the global one for that repo. Cheap to add, only loaded when relevant.

---

## 🔌 MCP Server (the only runtime component)

Built with `FastMCP`. Multi-client (Claude Code, Cursor, etc.) read/write the same store.

**Tools exposed:**

- `remember(name, body, tags, applies_to?)` — writes a new file under `conventions/` and appends to `INDEX.md`. The session agent (the one talking to you) supplies the structured args; the server writes `body` **verbatim**. See _How `remember` works_ below.
- `recall(query, tags?)` — ripgrep across files, returns matched snippets. Start text-only; add embeddings only if recall quality drops.
- `list_conventions(tags?)` — returns `INDEX.md` filtered by tag/stack.
- `forget(name)` — removes a file and its index entry.

No git hooks, no LLM distillation, no vector DB until proven necessary.

### How `remember` works

The MCP tool takes **already-structured args** — no separate LLM distiller. The agent in your current session does the structuring as part of its normal response, because it already has the conversation context.

Flow:

1. You tell the agent: _"we always use Pydantic v2 for boundary validation, remember that."_
2. Agent calls `remember(name="pydantic-validation", body="...", tags=["python","validation"])`. It picks the slug and tags from context; the `body` stays faithful to what you said.
3. Server writes the file verbatim and appends one line to `INDEX.md`.
4. Agent reports back: _"Saved as `pydantic-validation.md`."_

Why this shape:

- **No extra LLM call or cost** — structuring happens inside the existing agent turn.
- **Faithful body** — Claude Code shows tool calls before executing, so you see what's about to be saved and can correct it on the spot (_"no, add 'except for internal dataclasses'"_).
- **Same path from terminal** — `helix remember --name X --tags a,b "body"` calls the same MCP tool with explicit flags.
- **Editable after the fact** — it's just markdown, so `$EDITOR ~/.dev_brain/conventions/foo.md` works anytime. No reindexing (grep reads files fresh).

Confirmation policy: write-immediately by default. Claude Code's tool-call preview is the natural confirmation step. For clients that auto-approve tools, a server config flag can require an explicit `confirm=true` second call.

---

## 💻 CLI (thin wrapper, optional)

`Typer`-based. Same operations as the MCP tools, for terminal use:

- `helix remember "<text>" --tags python,async` — append a convention.
- `helix recall "<query>"` — search.
- `helix list [--tags python]` — print the filtered index.
- `helix serve` — start the MCP server.

---

## 🔁 Context Loading Strategy

**Hybrid: a tiny filtered index is always loaded; full bodies are on-demand.** This is the core token-efficiency decision and is non-negotiable in the design.

### Two layers

| Layer                               | Loaded when                                            | Typical size      |
| ----------------------------------- | ------------------------------------------------------ | ----------------- |
| `INDEX.md` (filtered by stack tags) | Session start                                          | ~20–50 one-liners |
| Full convention file                | Agent calls `recall()` or reads the file path directly | ~10–50 lines each |

### Why hybrid (not pure search)

Pure on-demand search has an "unknown unknowns" problem — the agent can't search for a convention if it doesn't know one exists. The filtered index is the agent's table of contents so it knows _what to look up_. Without it, a "prefer Pydantic" note is invisible until you re-mention Pydantic, which defeats the whole point of the system.

### How the index enters context

**Default mechanism: tool-call at session start.** Each project's `CLAUDE.md` includes an instruction like:

> On the first turn, call `list_conventions(tags=[<this project's stack>])` to surface relevant global conventions.

This costs one MCP call per session and returns only the stack-relevant slice. Token cost stays bounded as the global store grows because tag filtering happens server-side.

Alternative mechanisms (not the default):

- **MCP resource:** expose `INDEX.md` as a FastMCP resource for auto-injection. Simpler, but unfiltered.
- **`@`-reference:** symlink `INDEX.md` into each repo and `@`-reference from `CLAUDE.md`. Adds per-project setup.

### What is **never** loaded in bulk

- The `conventions/` directory as a whole — even at 200+ files, only files the agent actively pulls enter context.
- Other-stack conventions — `tags=[<stack>]` filtering excludes them entirely.

### Per-session flow

1. Session starts → agent calls `list_conventions(tags=["python"])` → ~30 one-liners enter context.
2. User asks for something. Agent scans the one-liners, spots a relevant entry.
3. If the one-liner is enough → agent applies it directly. No further calls.
4. If full reasoning is needed → `recall("<name>")` pulls that single file's body.

### Other efficiency choices

- **Tag-filter by stack** so a Python project never sees TypeScript conventions.
- **Verbatim notes** (no LLM rewriting) — keeps content short and faithful to what you actually said.

---

## 🪜 Build Order

Ship the smallest useful version first. Each step is ~1 evening.

1. **Step 1 — Folder + CLI.** Create `~/.dev_brain/`, write `helix remember` and `helix list`. Use it manually for a week to validate the workflow.
2. **Step 2 — MCP server.** Wrap the same operations in `FastMCP`. Point Claude Code (and Cursor) at it.
3. **Step 3 — Project overrides.** Add the `projects/<repo>/` shadow layer if real conflicts emerge.
4. **Step 4 (maybe never) — Embeddings.** Only if ripgrep recall becomes the bottleneck. At <500 short files, this is unlikely.

---

## 💻 Tech Stack

| Component      | Technology            |
| :------------- | :-------------------- |
| **CLI**        | `Typer`               |
| **MCP Server** | `FastMCP`             |
| **Search**     | `ripgrep` (shell out) |
| **Storage**    | Plain markdown files  |

Deliberately **not** in the stack: Milvus, vector embeddings, LLM distillers, Tree-sitter, GitPython, MarkItDown. Add only if a concrete need appears.

---

## 🚫 Explicit Non-Goals

- No synthesis/distillation — verbatim wins for convention notes.
- No per-commit re-indexing — conventions don't change with commits; the `remember` call is the trigger.
- No duplication of Claude Code's per-project auto-memory — Helix is the **global** layer only.
- No semantic search until grep proves insufficient.

## ✅ TODO

Track build progress here. Items mirror the Build Order phases.

### Step 1 — Folder + CLI (MVP)

     Track build progress here. Items mirror the Build Order phases.

     ### Step 1 — Folder + CLI (MVP)
     - [x] Init Python project (`pyproject.toml`, add `typer` dep)
     - [x] Create `~/.dev_brain/` skeleton on first run: `conventions/`, empty `INDEX.md`
     - [x] Define frontmatter schema (`name`, `tags`, `applies_to`) + a tiny parser
     - [x] `helix remember <slug> "<body>" --tags a,b` → write `conventions/<slug>.md` verbatim, append one line to `INDEX.md`
     - [x] `helix list [--tags python]` → print filtered `INDEX.md`
     - [x] `helix recall "<query>" [--tags ...]` → search conventions, return matched snippets with file paths
     - [x] `helix forget <slug>` → remove file + its `INDEX.md` line
     - [x] `helix install` / `helix uninstall` → interactive menu (no client/scope flags) that:
       - auto-detects installed clients (Claude Code, Cursor, Codex CLI, opencode)
       - prompts for one-or-more clients (multi-select) + scope (global vs project)
       - writes an idempotent snippet wrapped in `<!-- helix:start -->` / `<!-- helix:end -->` markers so re-runs update in place
       - warns if `helix` is not on PATH (the snippet's `helix list` call would otherwise fail); detection only, no PATH/shell mutation
       - Step 1 snippet: *"run `helix list` at session start"*; Step 2 will swap in the MCP `list_conventions` instruction

     ### Step 2 — MCP Server
     - [x] Add `fastmcp` dep
     - [x] Wrap `remember`, `recall`, `list_conventions`, `forget` as MCP tools (shared core with CLI)
     - [x] `helix serve` command to launch the MCP server
     - [x] Write a `CLAUDE.md` snippet: instruct agent to call `list_conventions(tags=[<stack>])` on first turn
     - [x] Document Claude Code + Cursor MCP config to point at `helix serve`
     - [x] Extend `helix install` to also write each selected client's MCP server
       config (pointing at `helix serve`) alongside the instruction snippet —
       same multi-select/scope flow, idempotent, per-client config format
       (e.g. `.mcp.json`, Cursor `mcp.json`, `~/.codex/config.toml`)
     - [x] Decide confirmation policy default (write-immediately) and config flag for clients that auto-approve

     ### Step 3 — Project Overrides
     - [ ] Detect current repo name (git remote URL or cwd basename)
     - [ ] Load `projects/<repo>/` files and shadow global files with matching `name:`
     - [ ] Surface overrides distinctly in `list_conventions` output (e.g., `[override]` marker)
     - [ ] CLI: `helix push-global <slug>` to promote a project-local convention to global

     ### Step 4 — Embeddings (only if needed)
     - [ ] Measure: is `ripgrep` recall missing relevant conventions in practice?
     - [ ] If yes: add a local embedding index (sqlite + a small model) behind the same `recall()` interface
     - [ ] Keep ripgrep as fallback / hybrid

     ### Cross-cutting
     - [ ] Tests for the frontmatter parser and `INDEX.md` writer (the only logic with real correctness risk)
     - [ ] `helix doctor` command: sanity-check store integrity (orphaned files, broken index lines)
     - [ ] README with install + first-run walkthrough

     Verification

     - Open docs/PLAN.md and confirm the new ## ✅ TODO section appears at the end, no existing content modified.
     - The checkboxes parse correctly in any markdown renderer.
