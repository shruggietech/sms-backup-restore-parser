# CLAUDE.md — sms-backup-parser

## Project Identity

CLI utility for parsing [SyncTech SMS Backup & Restore](https://www.synctech.com.au/sms-backup-restore/) XML exports. Converts SMS, MMS, and call log XML into structured JSON and generates built-in analytical reports. Distributed as standalone executables for Windows and Ubuntu.

## Authoritative References

- **Upstream field definitions**: https://www.synctech.com.au/sms-backup-restore/fields-in-xml-backup-files/
- **Upstream XSD**: https://synctech.com.au/wp-content/uploads/2018/01/sms.xsd_.txt
- **Local schema**: `sms-backup-restore.schema.json` — JSON Schema (draft-07) derived from upstream field definitions. This is the project's source of truth for field names, types, and enum semantics. The current version is a Gemini-generated draft and is expected to undergo significant revision and completion.
- **Local reference material**: `./reference/SyncTech-docs/` and `./reference/SyncTech-utilities/` contain offline PDF prints and files distributed by SyncTech. This material is **not licensed for redistribution** and must never be committed to a public repository. It exists solely to inform the creation of `./reference/knowledge-base.md` (see below), after which the source directories will be deleted.
- **Knowledge base**: `./reference/knowledge-base.md` — An unofficial, original-prose condensation of all relevant technical details from the SyncTech reference material. Written in Markdown. Must be composed entirely in our own words to avoid IP concerns. This file *is* safe for version control and long-term retention.

When upstream docs and the local schema conflict, defer to the local schema. Update the schema deliberately when upstream changes warrant it.

## Repository Layout

```
.
├── CLAUDE.md                          # This file
├── LICENSE                            # Apache License 2.0
├── CHANGELOG.md                       # Change log — update with every meaningful change
├── README.md                          # Project overview and quick start
├── .gitignore                         # VCS exclusions — keep current
├── pyproject.toml                     # PEP 621 metadata, build config, tool settings
├── mkdocs.yml                         # MkDocs documentation site config
├── sms-backup-restore.schema.json     # JSON Schema (draft-07) — source of truth
├── sms-backup-restore-parser.code-workspace  # VS Code workspace config
├── src/
│   └── sms_backup_parser/             # Main package (importable as sms_backup_parser)
│       ├── __init__.py                # Package version
│       ├── __main__.py                # python -m support
│       ├── cli.py                     # argparse CLI entry point
│       ├── parser.py                  # Streaming XML → JSON transformer
│       ├── reports.py                 # Summary, contacts, and timeline reports
│       ├── models.py                  # Enum constants and lookup tables
│       ├── utils.py                   # Shared helpers (date conversion, formatting)
│       ├── progress.py                # Progress reporting for long parses
│       └── validate.py                # Optional JSON Schema validation
├── tests/                             # pytest test suite
│   ├── fixtures/                      # Synthetic XML test data
│   ├── test_parser.py
│   ├── test_cli.py
│   ├── test_reports.py
│   ├── test_utils.py
│   └── test_models.py
├── scripts/
│   └── build.py                       # PyInstaller build script
├── docs/                              # MkDocs documentation (GitHub Pages)
├── reference/
│   ├── knowledge-base.md              # Distilled technical reference — safe for VCS
│   ├── SyncTech-docs/                 # PDFs etc. — DO NOT COMMIT, delete after KB is built
│   └── SyncTech-utilities/            # Utilities — DO NOT COMMIT, delete after KB is built
└── ...
```

## Current State

The parser and schema have been rewritten from the original Gemini drafts. The schema now has full field coverage from the upstream XSD. The parser streams records with constant memory usage. The CLI is functional with `parse`, `report`, and `version` subcommands. Tests pass (47/47). Build and documentation infrastructure are in place.

## Tech Stack & Constraints

- **Python 3.12+**. Target the current stable release features.
- **Virtual environment required.** All development — running the parser, tests, builds, doc generation — must happen inside a venv. Do not install project dependencies into the system Python. Create the venv at `.venv/` in the project root. The `.gitignore` already excludes it.
- Stdlib-only is preferred for the core parse path, but **do not treat external dependencies as a last resort.** If a library meaningfully improves output quality, report generation, CLI ergonomics, or build tooling, use it. Just be deliberate — state what the dep buys and pin versions.
- Outputs include both **structured JSON files** (for downstream tooling: DuckDB, jq, custom scripts, etc.) and **built-in reports** generated natively by the CLI.
- Build targets: standalone **Windows `.exe`** and **Ubuntu-compatible binary** (PyInstaller, Nuitka, or equivalent — evaluate at build time).

## Commands

```bash
# Set up venv and install (first time)
python -m venv .venv
source .venv/bin/activate   # or .venv\Scripts\activate on Windows
pip install -e ".[dev]"     # editable install with pytest

# Parse XML to JSON (separate per-type files)
python -m sms_backup_parser parse backup.xml -o ./output/

# Parse to single combined file, strip media
python -m sms_backup_parser parse backup.xml --combined --strip-media

# Generate summary report from parsed JSON
python -m sms_backup_parser report output/backup.json -t summary

# Run tests
pytest tests/

# Build standalone executable
pip install pyinstaller
python scripts/build.py
```

## Architecture Decisions

### Streaming parse (`iterparse`)
XML exports from SMS Backup & Restore are routinely hundreds of megabytes to multiple gigabytes. The parser uses `ET.iterparse` with `elem.clear()` to avoid loading the full DOM. **Do not refactor to `ET.parse()` or full-tree approaches.**

### Flat attribute extraction
SMS and call records map 1:1 from XML attributes to JSON object keys via `dict(elem.attrib)`. MMS records additionally collect nested `<part>` and `<addr>` child elements into arrays. Preserve this pattern — do not invent ORM-style classes or dataclass wrappers unless the project explicitly moves to that.

### `date_iso` injection
The parser injects a computed `date_iso` field (ISO 8601, UTC) from the Java-epoch-millisecond `date` field. This is a convenience field for human readability and tooling interop. The raw `date` field is always preserved.

### Schema governs output
All JSON output must validate against `sms-backup-restore.schema.json`. If you add fields, update the schema first, then the parser.

### Dual output philosophy
The CLI produces two categories of output:
1. **Raw JSON** — faithful structured export of the XML data, stored to disk, schema-validated. This is the interchange format for downstream consumers.
2. **Reports** — human-readable analytical output generated natively by the tool (summaries, per-contact stats, timelines, etc.). Report formats and content will evolve with the project.

These are not mutually exclusive. A single invocation may produce both.

## CLI Requirements

The final product is a polished command-line utility, not a bare script. It must meet these standards:

- **`argparse`-based** (or `argparse`-compatible alternative if justified). Full subcommand support if the surface area warrants it.
- **Thorough `--help` text** at every level — top-level, per-subcommand, and per-argument. Help strings must be descriptive, not terse placeholders.
- **Meaningful parameter aliases**: every frequently-used flag gets both a short form and a long form (e.g., `-o` / `--output`, `-v` / `--verbose`, `-q` / `--quiet`).
- **Verbosity control**: default output is clean and informative. `-v` / `--verbose` adds operational detail (files opened, record counts, timing). `-q` / `--quiet` suppresses all non-error output. These are mutually exclusive.
- **Exit codes**: 0 on success, 1 on user error (bad args, missing files), 2 on parse/data errors. Document these in help text.
- **Progress feedback**: for long-running operations on large files, provide periodic progress indicators (record counts, elapsed time) at default verbosity. Suppressed by `--quiet`.

## Distribution & Build

- Standalone executables for **Windows (`.exe`)** and **Ubuntu (ELF binary)**.
- Evaluate PyInstaller, Nuitka, or similar at build time. Document the chosen approach and any platform-specific build steps.
- The executable must be fully self-contained — no assumption of a Python installation on the target system.
- Build and release scripts live in `scripts/`. Include at minimum a script for producing the Windows and Ubuntu binaries.

## Coding Conventions

- **No type stubs or heavy typing unless asked.** Light type hints on function signatures are fine.
- **Docstrings**: imperative mood, one-liner for simple functions. Numpy/Google-style only if the function is complex enough to warrant structured docs.
- **Error handling**: fail loud. `try/except` blocks must not swallow exceptions silently. Print or log the error context and re-raise or exit nonzero.
- **File I/O**: always specify `encoding='utf-8'` explicitly.
- **Naming**: snake_case everywhere. No Hungarian notation. Module names are short lowercase nouns or verb-noun pairs (`parser.py`, `analyze.py`, `export_csv.py`).
- **Project structure**: follow the `src/` layout. The importable package is `sms_backup_parser` under `src/sms_backup_parser/`. Do not put application code in the project root.
- **Tests**: `pytest`. Put tests in `tests/`. Mirror the source module name (`test_parser.py`). No test file without at least one assertion.

## Changelog

Maintain a `CHANGELOG.md` in the repository root. Update it with every meaningful change — new features, bug fixes, schema changes, CLI interface changes, and non-trivial refactors. Do not log typo fixes, comment edits, or purely internal renames.

Follow [Keep a Changelog](https://keepachangelog.com/) format:
- Group entries under `Added`, `Changed`, `Fixed`, `Removed` as appropriate.
- Newest entries go at the top under an `## [Unreleased]` section.
- When a version is tagged for release, move `[Unreleased]` entries under a dated version heading (e.g., `## [0.1.0] - 2026-03-17`).
- Each entry is a single concise line describing the change from the user's perspective.

**This is not optional.** Every task that modifies behavior, output, or the public interface must include a corresponding `CHANGELOG.md` update before the work is considered complete.

## Behavioral Directives

- Treat this as a peer collaboration. Do not pad responses with caveats about "best practices" unless something is actually wrong.
- When modifying existing files, show the precise change. Do not rewrite entire files to fix a three-line bug.
- If a task is ambiguous, ask one clarifying question before proceeding. Do not guess at intent and produce speculative output.
- The schema is the contract. Do not add, rename, or remove fields from JSON output without updating the schema to match.
- Bash one-liners and `jq` pipelines are first-class tools here. Suggest them freely for ad hoc data inspection.

## Data Sensitivity

Backup exports contain PII: phone numbers, contact names, message bodies, timestamps, and base64-encoded media. **Never commit sample data or real exports to version control.** Test fixtures must use synthetic/anonymized data.

The `./reference/SyncTech-docs/` and `./reference/SyncTech-utilities/` directories contain material we do not have redistribution rights for. Delete the SyncTech directories once the knowledge base is complete.

### `.gitignore`

A `.gitignore` must exist in the repository root and must be kept current. At minimum it must exclude:
- `reference/SyncTech-docs/` and `reference/SyncTech-utilities/` (unlicensed material)
- Real XML backup exports and any file containing PII
- Build artifacts (`*.exe`, `dist/`, `build/`)
- Standard Python artifacts (`__pycache__/`, `*.pyc`, `.eggs/`, `*.egg-info/`)

When adding new tooling, dependencies, or build steps that produce ignorable artifacts, update `.gitignore` in the same change.

## License

This project is licensed under the **Apache License 2.0**. A `LICENSE` file must exist in the repository root containing the standard Apache 2.0 text. All source files may optionally include the short-form Apache header, but this is not required unless the project grows to include contributions from multiple parties.

## Documentation

The `docs/` directory hosts the project's public-facing documentation, served via **GitHub Pages**. This may include:
- A project landing page / README-style overview
- MkDocs-generated documentation (if adopted — evaluate when the CLI surface is stable)
- Usage examples, report format descriptions, and schema documentation

The docs site is a deliverable, not an afterthought. When a user-facing feature is complete, corresponding documentation is expected before the work is considered done.

## Planned Evolution

Future work may include any of: per-contact conversation threading, media extraction from MMS base64 parts, DuckDB/Parquet export for OLAP queries, timeline visualizations, richer report types, and integration with the broader ShruggieTech toolchain. Do not pre-build these — implement when tasked.
