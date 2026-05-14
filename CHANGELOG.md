# CHANGELOG


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
