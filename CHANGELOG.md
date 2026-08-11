# CHANGELOG


## v6.0.0 (2026-08-10)

### Bug Fixes

- Correct per-client MCP config shapes and guard bad config files
  ([#17](https://github.com/justmatias/helix/pull/17),
  [`f48b25b`](https://github.com/justmatias/helix/commit/f48b25b5ca33c294fbb6c0fdecc5f7d36bc6a0ab))

* fix: correct per-client MCP config shapes and guard bad config files

Reviewed each client's actual MCP config contract instead of assuming a shared JSON shape:

- opencode uses a `mcp` key with a `local`/command-array server shape, not the generic `mcpServers`
  object Claude/Cursor use — Helix was silently writing an entry opencode's schema doesn't
  recognize. - Codex's TOML table is now wrapped in `# helix-mcp:start/end` markers (mirroring the
  markdown snippet convention), so a hand-added `env` line inside the block no longer defeats
  uninstall's exact-match. - Claude Code's global MCP scope lives in ~/.claude.json, which also
  holds live session state; when the `claude` CLi is on PATH, delegate to `claude mcp add/remove -s
  user` instead of rewriting that file. - Malformed existing config/hook files raise
  InvalidConfigError with the offending path instead of a bare JSONDecodeError traceback; the CLI
  catches it per-client and continues instead of aborting install. - detect_snippet_blocks now also
  finds MCP/hook entries left behind after the markdown snippet was deleted by hand, so uninstall
  doesn't leak them.

Also collapsed the duplicated JSON-parsing and leftover-detection helpers this introduced across
  mcp_config.py/hooks.py/operations.py into shared functions, and one `_guarded()` wrapper replacing
  four repeated try/except blocks in the CLI.

Co-Authored-By: Claude Sonnet 5 <noreply@anthropic.com>

* refactor: simplify config-error guard and move it to utils/io

Replace _guarded(partial(...)) with warn_on_invalid_config(func, *args), dropping the
  functools.partial indirection. Relocate it from cli/commands.py to utils/io.py since it's a
  generic call-and-warn helper, not CLI-specific.

* refactor: enforce named args in warn_on_invalid_config

Switch from *args to **kwargs so call sites must name each argument, making the wrapped
  install/uninstall calls readable.

* refactor: address PR #17 review comments

- Turn warn_on_invalid_config into a decorator applied once at the CLI boundary, instead of a
  call-site wrapper that took the target function and its kwargs — call sites now read as plain
  calls. - Split read_json out of errors.py into its own json_config.py, keeping errors.py to just
  the exception it's named for. - Note why McpConfigFormat.OPENCODE is a distinct shape, not a
  made-up format: opencode's schema uses mcp.<name> with a local/command-array shape, unlike the
  generic mcpServers object other JSON clients accept.

* test: extract reusable claude-CLI and settings fixtures

Pulls the repeated shutil.which/subprocess.run monkeypatching for the claude-CLI delegation tests,
  and the repeated "foreign settings" JSON seed in test_hooks.py, into conftest fixtures
  (_claude_cli_available, _claude_cli_unavailable, claude_cli_calls, _write_foreign_settings).

* refactor: split mcp_config.py's merge/remove logic by format

_merge and _remove each mixed JSON-dict manipulation and TOML-text regex substitution in one
  function per operation, so reviewing either meant context-switching between two unrelated data
  shapes mid-function.

Split into _merge_json_entry/_merge_toml_block and _remove_json_entry/_remove_toml_block, with
  _merge/_remove reduced to thin dispatchers. JSON and OPENCODE now share one code path driven by a
  JSON_SHAPE_BY_FORMAT lookup (top-level key + entry shape per format) instead of parallel if/elif
  branches.

---------

Co-authored-by: Claude Sonnet 5 <noreply@anthropic.com>

### Features

- Breaking change detected [skip ci]
  ([`7aee7d6`](https://github.com/justmatias/helix/commit/7aee7d6ffc67a3dc53f6e67ad7659e8b9dcaa2c6))

- Breaking change detected [skip ci]
  ([`f18de42`](https://github.com/justmatias/helix/commit/f18de4274f10b76cf837c951939e399aaef60371))

- Cut friction in capture, install, and recall ([#16](https://github.com/justmatias/helix/pull/16),
  [`eb8d1ca`](https://github.com/justmatias/helix/commit/eb8d1ca06615e5969320ffa4c148f1b6b3a8d7fd))

* feat: cut friction in capture, install, and recall

Every path in and out of Helix cost more than it should:

- `remember` derives the name from the body; `-` reads stdin and no argument opens $EDITOR, so
  capturing a convention is one line. - `install` writes a Claude Code SessionStart hook, so the
  index is injected into every session instead of depending on the agent following the CLAUDE.md
  snippet (now trimmed to the write path). - `install`/`uninstall` take --client/--scope/--yes and
  can run unattended; `uninstall` now also removes the MCP config it wrote. - `recall` returns whole
  conventions instead of path:lineno:line fragments that had no follow-up tool. - HELIX_BRAIN_DIR
  relocates the store to a directory you already sync. - `helix edit <name>` opens a convention and
  refreshes its index line. - Drop `applies_to`: written to frontmatter, never read by any filter.

Co-Authored-By: Claude Opus 5 <noreply@anthropic.com>

* chore(config): update pre-commit hooks

* refactor: improve readability of installation_directory and hook_path_for methods

* refactor: address PR #16 review comments

- Split per-client Client() definitions into helix/core/installer/clients/ (one module per client)
  so client-specific config is easy to find and edit; shared install/hook/MCP logic stays generic
  since it already no-ops for clients that don't set a given path. - Move install/uninstall
  orchestration and client selection out of commands.py into a dedicated helix/cli/install.py
  module. - Move body-resolution (argument/stdin/$EDITOR) out of commands.py into a reusable
  helix.utils.resolve_text_argument helper. - Move the "convention" fallback name into
  Brain.free_name so callers don't need to know its default. - Simplify Brain.recall's list
  comprehension into a named _matches check. - Make _select_clients take keyword-only arguments. -
  Fix test_cmd_install_no_detected_clients_lists_all, which was missing the working_dir fixture and
  wrote real install files into the repo root when run.

Co-Authored-By: Claude Sonnet 5 <noreply@anthropic.com>

* refactor: move install/uninstall back into commands.py, share select_clients

Merge helix/cli/install.py back into commands.py per feedback, and move select_clients (formerly
  _select_clients) into prompts.py as a public, reusable helper alongside pick/pick_many.

* refactor: simplify client selection logic in select_clients function

* test: extract reusable setup logic into fixtures

Pull repeated install_hook/uninstall_hook and Brain.remember seed calls out of test bodies and into
  conftest fixtures, following the project's usefixtures convention for side-effect-only setup.

* chore: fix circular imports

* refactor: rename fixture for clarity and consistency

* refactor: inline hook-entry helpers in hooks.py

Removes _is_helix_entry and _prune as standalone module-level functions, folding their logic
  directly into install_hook/uninstall_hook.

---------

Co-authored-by: Claude Opus 5 <noreply@anthropic.com>

Co-authored-by: github-actions[bot] <github-actions[bot]@users.noreply.github.com>


## v4.1.4 (2026-08-09)

### Bug Fixes

- **deps**: Bump cryptography from 48.0.1 to 50.0.0
  ([#15](https://github.com/justmatias/helix/pull/15),
  [`b531ef3`](https://github.com/justmatias/helix/commit/b531ef37f9a5c45c142ca06aa791cafc762b7ea3))

* fix(deps): bump cryptography from 48.0.1 to 50.0.0

Bumps [cryptography](https://github.com/pyca/cryptography) from 48.0.1 to 50.0.0. -
  [Changelog](https://github.com/pyca/cryptography/blob/main/CHANGELOG.rst) -
  [Commits](https://github.com/pyca/cryptography/compare/48.0.1...50.0.0)

--- updated-dependencies: - dependency-name: cryptography dependency-version: 50.0.0

dependency-type: indirect ...

Signed-off-by: dependabot[bot] <support@github.com>

* chore(config): update pre-commit hooks

---------

Co-authored-by: dependabot[bot] <49699333+dependabot[bot]@users.noreply.github.com>

Co-authored-by: github-actions[bot] <github-actions[bot]@users.noreply.github.com>

- **deps**: Bump joserfc from 1.6.7 to 1.6.8 ([#12](https://github.com/justmatias/helix/pull/12),
  [`1fa8c74`](https://github.com/justmatias/helix/commit/1fa8c74081313f9e28e910b88f84f673d6866410))

Bumps [joserfc](https://github.com/authlib/joserfc) from 1.6.7 to 1.6.8. - [Release
  notes](https://github.com/authlib/joserfc/releases) -
  [Changelog](https://github.com/authlib/joserfc/blob/main/docs/changelog.rst) -
  [Commits](https://github.com/authlib/joserfc/compare/1.6.7...1.6.8)

--- updated-dependencies: - dependency-name: joserfc dependency-version: 1.6.8

dependency-type: indirect ...

Signed-off-by: dependabot[bot] <support@github.com>

Co-authored-by: dependabot[bot] <49699333+dependabot[bot]@users.noreply.github.com>

- **deps**: Bump mcp from 1.27.1 to 1.28.1 ([#14](https://github.com/justmatias/helix/pull/14),
  [`d01924e`](https://github.com/justmatias/helix/commit/d01924e647919231f565d41961d01b60330f1a77))

* fix(deps): bump mcp from 1.27.1 to 1.28.1

--- updated-dependencies: - dependency-name: mcp dependency-version: 1.28.1

dependency-type: indirect ...

Signed-off-by: dependabot[bot] <support@github.com>

* chore(config): update pre-commit hooks

---------

Co-authored-by: dependabot[bot] <49699333+dependabot[bot]@users.noreply.github.com>

Co-authored-by: github-actions[bot] <github-actions[bot]@users.noreply.github.com>

### Chores

- Update uv version
  ([`039887b`](https://github.com/justmatias/helix/commit/039887bef7b83a3aa84b95552cad3b9f79c76a6c))


## v4.1.3 (2026-06-25)

### Bug Fixes

- **deps**: Bump pydantic-settings from 2.14.1 to 2.14.2
  ([#11](https://github.com/justmatias/helix/pull/11),
  [`1fda74e`](https://github.com/justmatias/helix/commit/1fda74eba67924761621a3ce8cf26e50f02afd62))

* fix(deps): bump pydantic-settings from 2.14.1 to 2.14.2

Bumps [pydantic-settings](https://github.com/pydantic/pydantic-settings) from 2.14.1 to 2.14.2. -
  [Release notes](https://github.com/pydantic/pydantic-settings/releases) -
  [Commits](https://github.com/pydantic/pydantic-settings/compare/v2.14.1...v2.14.2)

--- updated-dependencies: - dependency-name: pydantic-settings dependency-version: 2.14.2

dependency-type: direct:production ...

Signed-off-by: dependabot[bot] <support@github.com>

* chore(config): update pre-commit hooks

* chore(ci): add pre-commit hook synchronization and stage all changes for hook updates

---------

Co-authored-by: dependabot[bot] <49699333+dependabot[bot]@users.noreply.github.com>

Co-authored-by: github-actions[bot] <github-actions[bot]@users.noreply.github.com>

Co-authored-by: Matias Gimenez <matiasgimenez.dev@gmail.com>


## v4.1.2 (2026-06-25)

### Bug Fixes

- **deps**: Bump actions/checkout from 6 to 7 ([#10](https://github.com/justmatias/helix/pull/10),
  [`3a026c4`](https://github.com/justmatias/helix/commit/3a026c4dec42b768076dee1f6b3b698a5d58a9ff))

* fix(deps): bump actions/checkout from 6 to 7

Bumps [actions/checkout](https://github.com/actions/checkout) from 6 to 7. - [Release
  notes](https://github.com/actions/checkout/releases) -
  [Changelog](https://github.com/actions/checkout/blob/main/CHANGELOG.md) -
  [Commits](https://github.com/actions/checkout/compare/v6...v7)

--- updated-dependencies: - dependency-name: actions/checkout dependency-version: '7'

dependency-type: direct:production

update-type: version-update:semver-major ...

Signed-off-by: dependabot[bot] <support@github.com>

* chore(config): update pre-commit hooks

---------

Co-authored-by: dependabot[bot] <49699333+dependabot[bot]@users.noreply.github.com>

Co-authored-by: github-actions[bot] <github-actions[bot]@users.noreply.github.com>


## v4.1.1 (2026-06-18)

### Bug Fixes

- **deps**: Bump python-multipart from 0.0.29 to 0.0.31
  ([#7](https://github.com/justmatias/helix/pull/7),
  [`17957db`](https://github.com/justmatias/helix/commit/17957db01131fe55914bb3c41754c052a641d6a0))

Bumps [python-multipart](https://github.com/Kludex/python-multipart) from 0.0.29 to 0.0.31. -
  [Release notes](https://github.com/Kludex/python-multipart/releases) -
  [Changelog](https://github.com/Kludex/python-multipart/blob/main/CHANGELOG.md) -
  [Commits](https://github.com/Kludex/python-multipart/compare/0.0.29...0.0.31)

--- updated-dependencies: - dependency-name: python-multipart dependency-version: 0.0.31

dependency-type: indirect ...

Signed-off-by: dependabot[bot] <support@github.com>

Co-authored-by: dependabot[bot] <49699333+dependabot[bot]@users.noreply.github.com>

### Chores

- Update hookpin pre-commit hook and bump helix-memory version to 4.1.0
  ([`a4947ae`](https://github.com/justmatias/helix/commit/a4947ae1ef6ca6136b847a3d66a4e55227e68872))

- **deps**: Bump cryptography from 48.0.0 to 48.0.1
  ([#8](https://github.com/justmatias/helix/pull/8),
  [`3ce70ac`](https://github.com/justmatias/helix/commit/3ce70ac6637a335a372a503513fc97441caf7cc9))

Bumps [cryptography](https://github.com/pyca/cryptography) from 48.0.0 to 48.0.1. -
  [Changelog](https://github.com/pyca/cryptography/blob/main/CHANGELOG.rst) -
  [Commits](https://github.com/pyca/cryptography/compare/48.0.0...48.0.1)

--- updated-dependencies: - dependency-name: cryptography dependency-version: 48.0.1

dependency-type: indirect ...

Signed-off-by: dependabot[bot] <support@github.com>

Co-authored-by: dependabot[bot] <49699333+dependabot[bot]@users.noreply.github.com>

- **deps**: Bump starlette from 1.1.0 to 1.3.1 ([#9](https://github.com/justmatias/helix/pull/9),
  [`0aabbe5`](https://github.com/justmatias/helix/commit/0aabbe536efd6ab593112330c8b7ae8e664e0baa))

Bumps [starlette](https://github.com/Kludex/starlette) from 1.1.0 to 1.3.1. - [Release
  notes](https://github.com/Kludex/starlette/releases) -
  [Changelog](https://github.com/Kludex/starlette/blob/main/docs/release-notes.md) -
  [Commits](https://github.com/Kludex/starlette/compare/1.1.0...1.3.1)

--- updated-dependencies: - dependency-name: starlette dependency-version: 1.3.1

dependency-type: indirect ...

Signed-off-by: dependabot[bot] <support@github.com>

Co-authored-by: dependabot[bot] <49699333+dependabot[bot]@users.noreply.github.com>


## v4.1.0 (2026-05-24)

### Features

- Implement MCP tools for managing memory with list, remember, fo…
  ([#6](https://github.com/justmatias/helix/pull/6),
  [`4975db2`](https://github.com/justmatias/helix/commit/4975db2236b9f32ebfe628425028983f11f93292))

* feat: implement MCP tools for managing memory with list, remember, forget, and recall capabilities

* chore(config): update pre-commit hooks

* fix: refactor MCP tools for modular registration and add `helix serve` command

* docs: update MCP development plan and expand installation documentation for Claude Code and Cursor

* test: add tests for MCP tools.

* test: fix recall tool tests

* test: fix tests

* fix: implement idempotent mcp server configuration installation and uninstallation for client
  environments

* chore(docs): update implementation plan

* feat: implement HELIX_REQUIRE_CONFIRM setting to require explicit confirmation for remember and
  forget operations

* test: add coverage exclusions to MCP server and clean up unused pytest configurations and fixtures

* chore: add pragma no cover

* test: add edge case coverage for uninstall_mcp_config with empty or missing server definitions

---------

Co-authored-by: github-actions[bot] <github-actions[bot]@users.noreply.github.com>


## v4.0.3 (2026-05-19)

### Bug Fixes

- Add preamble and detect_path attributes to Client model; update installation logic and tests for
  cursor client ([#5](https://github.com/justmatias/helix/pull/5),
  [`0a003a1`](https://github.com/justmatias/helix/commit/0a003a1579a3aac5a36059f9e29497b4918540fa))


## v4.0.2 (2026-05-19)

### Bug Fixes

- Integrate questionary for interactive CLI prompts and update dep…
  ([#4](https://github.com/justmatias/helix/pull/4),
  [`8b6f7bb`](https://github.com/justmatias/helix/commit/8b6f7bb07ec047701dfaeb8207417137ea0aee73))

* fix: integrate questionary for interactive CLI prompts and update dependencies

* chore: fix mypy issues


## v4.0.1 (2026-05-19)

### Bug Fixes

- **docs**: Update quickstart docs
  ([`f16da2b`](https://github.com/justmatias/helix/commit/f16da2b8a34d732e6da7c5d13a4f6dce44bec57b))

### Chores

- Update project name to 'helix-memory', version to 4.0.0, and a…
  ([#3](https://github.com/justmatias/helix/pull/3),
  [`a680c86`](https://github.com/justmatias/helix/commit/a680c86e5e83c695979f1d775cde18ebed73fa74))

* chore: update project name to 'helix-memory', version to 4.0.0, and adjust Python requirement to
  >=3.13; enhance installation instructions in README and CI workflow for PyPI publishing

* fix: add Snyk security scanning workflow for automated dependency checks

* chore: update Python requirement to >=3.13 and rename package to 'helix-memory' with version 4.0.0

* chore: update package version to reflect renaming to 'helix-memory'


## v4.0.0 (2026-05-19)

### Features

- Breaking change detected [skip ci]
  ([`ef40cce`](https://github.com/justmatias/helix/commit/ef40ccedbcb594d8bfa75fdc2b984e141cf84b1e))

- Enhance Helix CLI with installation and uninstallation commands…
  ([#2](https://github.com/justmatias/helix/pull/2),
  [`172ebf0`](https://github.com/justmatias/helix/commit/172ebf0ae3eb96e845cd005051fda93bed249e02))

* feat: enhance Helix CLI with installation and uninstallation commands for agent integration

* chore(config): update pre-commit hooks

* fix: refactor installer operations and reorganize modules

* chore: fix lint issues and refactor installer tests

* fix: extract prompt selection logic into separate functions for improved readability and
  reusability

* chore: remove comment

---------

Co-authored-by: github-actions[bot] <github-actions[bot]@users.noreply.github.com>


## v3.0.0 (2026-05-14)

### Chores

- Restructure CLI application and enhance convention management
  ([`78320e1`](https://github.com/justmatias/helix/commit/78320e1dd4ecf95bdc5c37b057ad8ac135ce2a92))

- Update CLI structure and enhance command definitions with type annotations
  ([`a2717a6`](https://github.com/justmatias/helix/commit/a2717a651c915192a647e7f5ed0dc51d6e8d950e))

### Features

- Breaking change detected [skip ci]
  ([`52eddd9`](https://github.com/justmatias/helix/commit/52eddd91dc8e68981ecf6b6ff957fbf0a3ed9a29))


## v2.0.0 (2026-05-14)

### Bug Fixes

- **ci**: Prevent semantic-release from re-triggering CI loop
  ([`7aa43ea`](https://github.com/justmatias/helix/commit/7aa43ea6f8eb81652eb7d99ae1facdc8aadcde6d))

Add [skip ci] to the release commit message so pushes from python-semantic-release do not trigger a
  new workflow run.

Co-Authored-By: Claude Sonnet 4.6 <noreply@anthropic.com>

### Features

- Breaking change detected [skip ci]
  ([`ed70a0d`](https://github.com/justmatias/helix/commit/ed70a0dc36f4e7b9d4ea43af2db93ede0e85b788))

- Implement CLI for convention management with commands to remember, list, recall, and forget
  conventions
  ([`77fb37b`](https://github.com/justmatias/helix/commit/77fb37bd18bfa11163619c6a416d1ebd48b4fa6d))


## v1.0.0 (2026-05-13)

### Bug Fixes

- Add convention class for managing conventions and enhance filtering functionality
  ([`3517cb3`](https://github.com/justmatias/helix/commit/3517cb36376f537c87f8b55ec822a3a4ce1815b2))

- Implement brain class for convention management and remove unused storage utilities
  ([`f795485`](https://github.com/justmatias/helix/commit/f795485643854557076a73949b290c75e8b93bd3))

- Update project configuration and enhance storage management functionality
  ([`2cf4993`](https://github.com/justmatias/helix/commit/2cf4993dd94ebe4d6cc1882d0656d588ed609ccb))

### Chores

- Add initial project structure with configuration files, README, and core functionality
  ([`fa05287`](https://github.com/justmatias/helix/commit/fa052873076828a4dd3c622ff5f9fba8a17b69a5))

- Add pre-commit dependency and update lock file with new packages
  ([`ce99c36`](https://github.com/justmatias/helix/commit/ce99c360602d23a5d701f1230f3ac077f3ca3c59))

- Disable pylint invalid-name warning
  ([`41c3c53`](https://github.com/justmatias/helix/commit/41c3c53049153d153b9dc7546fd6454f63cb88e3))

- Fix lint issues
  ([`1e94e90`](https://github.com/justmatias/helix/commit/1e94e90fa09d640f7501382e1e55658c04791c3b))

- Streamline _filter_index_lines_by_tags method for improved readability
  ([`9eb6dcc`](https://github.com/justmatias/helix/commit/9eb6dccde68c18fb1dae5b9a609e86b6f9543f7c))

- Update build system configuration to use hatchling and specify wheel target
  ([`4e9fc37`](https://github.com/justmatias/helix/commit/4e9fc3713c0c41a60e1af22918129938bb4b0d99))

- **docs**: Add implementation plan
  ([`b10b684`](https://github.com/justmatias/helix/commit/b10b684e9412c15db733fa3c6de65005c3107846))

- **release**: Release version 1.0.0
  ([`bc81d7f`](https://github.com/justmatias/helix/commit/bc81d7fa301c66ff1607542928fc38b75da265e7))

### Features

- Breaking change detected [skip ci]
  ([`1229f2e`](https://github.com/justmatias/helix/commit/1229f2efc35bec295ea609ea18d61de573f33ede))
