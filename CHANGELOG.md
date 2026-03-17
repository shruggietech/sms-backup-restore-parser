# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/), and this project adheres to [Semantic Versioning](https://semver.org/).

## [Unreleased]

### Added
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
- Normalized `repo_url` casing in `mkdocs.yml` to match canonical GitHub URL
- **pyproject.toml**: Added `docs` optional dependency group (`mkdocs>=1.6`, `mkdocs-material>=9.5`) for documentation toolchain

### Fixed
- **pyproject.toml**: Moved `classifiers` from under `[project.urls]` to `[project]` where it belongs (was causing `pip install -e` to fail)
- Combined JSON output (`--combined`) now correctly handles interleaved record types (e.g., SMS-MMS-SMS) by buffering each section independently
