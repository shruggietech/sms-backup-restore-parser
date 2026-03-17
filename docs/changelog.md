# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/), and this project adheres to [Semantic Versioning](https://semver.org/).

## [Unreleased]

_No unreleased changes._

## [0.1.3] - 2026-03-17

### Fixed
- **Report: CSV files no longer have empty lines between rows on Windows.** The output file was opened without `newline=''`, causing Python's csv module to double carriage returns (`\r\r\n`).
- **Report: `-t all` now writes separate files instead of concatenating into one.** When `-o` is provided, `-t all` produces `{stem}_summary`, `{stem}_contacts`, and `{stem}_timeline` files. Stdout still concatenates with separators.
- **Parse: Multi-file `--combined` output now uses `combined.json` stem.** Previously the output was named after the first input file, which was misleading. Single-file combined retains the input stem.

### Changed
- **Report: `--top-n` default changed from 20 to 0 (all contacts).** Pass `--top-n N` to limit the contacts report to the top N entries.
- **Report: `generate_report()` now always returns `dict[str, str]`.** Keyed by report type name, even for single-type requests. This is an internal API change.

### Added
- **CLI: Format/extension mismatch warning.** The CLI now warns on stderr when `--format` does not match the output file extension (e.g., `--format csv -o report.json`).
- **Tests: Report module tests** (`tests/test_reports.py`) covering return types, CSV/JSON/text output quality, `--top-n` behavior, and empty data handling.
- **Tests: CLI report integration tests** for split-file output, format mismatch warnings, and combined parse naming.
- **Tests: Lint test** (`tests/test_lint.py`) runs `ruff check` as part of the test suite to catch lint regressions.
- **Dev: ruff linter configuration** added to `pyproject.toml` (rules: E, F, W, I; line-length 100; target Python 3.12).

## [0.1.1] - 2026-03-17

### Fixed
- **CLI: Multi-file `--combined` now produces a single merged output.** Previously, passing multiple XML files with `--combined` wrote a separate JSON file per input, each with empty arrays for missing record types. Records from all inputs are now merged into one combined JSON file.
- **Build: PyInstaller binary now bundles `jsonschema`.** The `--validate` flag previously always failed in standalone binaries with an ImportError. The build script now installs the `[validate]` extra and passes `--hidden-import=jsonschema` to PyInstaller.
- **CLI: Exit codes now propagate correctly.** `__main__.py` was discarding the return value from `main()`, causing the process to always exit with code 0 regardless of errors.

### Added
- **Parser: `parse_backup_multi()` function** for merging multiple XML inputs into a single combined JSON output in one pass.
- **Tests: Writer unit tests** for `JsonArrayWriter` and `CombinedJsonWriter` (`tests/test_writers.py`).
- **Tests: Validate module tests** (`tests/test_validate.py`).
- **Tests: Multi-file combined mode tests**, compact output tests, exit code propagation tests, and CLI `--validate` flag tests.
- **Tests: Committed synthetic XML fixtures** to `tests/fixtures/`. Previously excluded by `.gitignore`.

## [0.1.0] - 2026-03-17

### Added
- **CI: GitHub Actions docs deployment workflow** — New `.github/workflows/docs.yml` auto-builds and deploys the MkDocs site to GitHub Pages on pushes to `main` that modify `docs/`, `mkdocs.yml`, or `CHANGELOG.md`. Matches shruggie-indexer convention.
- **Docs: XML Format Reference page** — New `docs/xml-reference.md` presenting the upstream XML backup format documentation for end users. Spec: §15.2.
- **Docs: Changelog page** — New `docs/changelog.md` synchronized from the root `CHANGELOG.md`. Spec: §15.3.
- Project scaffolding: src/ layout, pyproject.toml, LICENSE, CHANGELOG
- Knowledge base distilled from SyncTech reference material (`reference/knowledge-base.md`)
- Complete JSON Schema with full field coverage for SMS, MMS (including parts and addrs), and call records
- Streaming XML parser with constant-memory usage via iterparse — handles multi-GB files
- Separate and combined JSON output modes (`--combined`)
- `--strip-media` flag to omit base64 data from MMS parts
- `--no-date-iso` flag to skip computed ISO date fields
- Optional schema validation via `--validate` (requires `jsonschema`)
- CLI with `parse`, `report`, and `version` subcommands
- Verbose (`-v`) and quiet (`-q`) output modes with progress reporting
- Exit codes: 0 success, 1 user error, 2 parse/data error
- Report generators: summary, contacts, and timeline reports with text/CSV/JSON output
- PyInstaller build script (`scripts/build.py`) for Windows and Ubuntu standalone executables
- pytest test suite with 47 tests and synthetic XML fixtures
- MkDocs documentation site structure with usage guide, schema reference, and report docs
- README.md with quick start and CLI overview
- CLAUDE.md updated with complete repository layout, commands, and current project state
- `.github/copilot-instructions.md` for GitHub Copilot context
- `[project.urls]` in `pyproject.toml` (homepage, repository, issues, changelog)

### Changed
- **Spec: Technical specification revision** — Expanded `reference/knowledge-base.md` from a flat XML format reference into a full technical specification with numbered sections, front matter, ToC, parser architecture, CLI interface, report types, repository layout, and documentation site configuration. Spec: §1–§15.
- **Docs: MkDocs configuration alignment** — Updated `mkdocs.yml` with slate theme, navigation features, search highlighting, content tabs, and required Markdown extensions to match ShruggieTech conventions. Spec: §15.1.
- **Docs: pyproject.toml docs dependency group** — Added `docs` optional dependency group for `mkdocs` and `mkdocs-material`. Spec: §15.6.
- Normalized `repo_url` casing in `mkdocs.yml` to match canonical GitHub URL

### Fixed
- **pyproject.toml**: Moved `classifiers` from under `[project.urls]` to `[project]` where it belongs (was causing `pip install -e` to fail)
- Combined JSON output (`--combined`) now correctly handles interleaved record types (e.g., SMS-MMS-SMS) by buffering each section independently

[Unreleased]: https://github.com/shruggietech/sms-backup-restore-parser/compare/v0.1.1...HEAD
[0.1.1]: https://github.com/shruggietech/sms-backup-restore-parser/compare/v0.1.0...v0.1.1
[0.1.0]: https://github.com/shruggietech/sms-backup-restore-parser/releases/tag/v0.1.0
