# CHANGELOG


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
