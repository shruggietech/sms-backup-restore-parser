# Copilot Instructions — sms-backup-parser

## Project Identity

CLI utility for parsing [SyncTech SMS Backup & Restore](https://www.synctech.com.au/sms-backup-restore/) XML exports. Converts SMS, MMS, and call log XML into structured JSON and generates built-in analytical reports. Distributed as standalone executables for Windows and Ubuntu.

## Authoritative References

- **Upstream field definitions**: https://www.synctech.com.au/sms-backup-restore/fields-in-xml-backup-files/
- **Upstream XSD**: https://synctech.com.au/wp-content/uploads/2018/01/sms.xsd_.txt
- **Local schema**: `sms-backup-restore.schema.json` — JSON Schema (draft-07) derived from upstream field definitions. This is the project's source of truth for field names, types, and enum semantics.
- **Knowledge base**: `./reference/knowledge-base.md` — An unofficial, original-prose condensation of all relevant technical details from the SyncTech reference material.

When upstream docs and the local schema conflict, defer to the local schema. Update the schema deliberately when upstream changes warrant it.

## Repository Layout

```
.
├── CLAUDE.md                          # Claude Code instructions
├── LICENSE                            # Apache License 2.0
├── CHANGELOG.md                       # Change log — update with every meaningful change
├── README.md                          # Project overview and quick start
├── .gitignore                         # VCS exclusions — keep current
├── pyproject.toml                     # PEP 621 metadata, build config, tool settings
├── mkdocs.yml                         # MkDocs documentation site config
├── sms-backup-restore.schema.json     # JSON Schema (draft-07) — source of truth
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
│       └── validate.py               # Optional JSON Schema validation
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
│   ├── index.md                       # Site landing page
│   ├── installation.md                # Installation guide
│   ├── usage.md                       # CLI usage reference
│   ├── schema.md                      # JSON Schema reference
│   ├── xml-reference.md               # Upstream XML format reference
│   ├── reports.md                     # Report types documentation
│   └── changelog.md                   # Synced copy of root CHANGELOG.md
└── reference/
    └── knowledge-base.md              # Technical specification
```

## Tech Stack & Constraints

- **Python 3.12+**. Target the current stable release features.
- **Virtual environment required.** All development must happen inside a venv at `.venv/` in the project root. Do not install project dependencies into the system Python.
- Stdlib-only is preferred for the core parse path, but external dependencies are acceptable when they meaningfully improve output quality, report generation, CLI ergonomics, or build tooling. Pin versions for any added dependency.
- Outputs include both **structured JSON files** (for downstream tooling: DuckDB, jq, custom scripts, etc.) and **built-in reports** generated natively by the CLI.
- Build targets: standalone **Windows `.exe`** and **Ubuntu-compatible binary** via PyInstaller.

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
XML exports are routinely hundreds of megabytes to multiple gigabytes. The parser uses `ET.iterparse` with `elem.clear()` to avoid loading the full DOM. Do not refactor to `ET.parse()` or full-tree approaches.

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

- **`argparse`-based** with full subcommand support.
- **Thorough `--help` text** at every level — top-level, per-subcommand, and per-argument. Help strings must be descriptive, not terse placeholders.
- **Meaningful parameter aliases**: every frequently-used flag gets both a short form and a long form (e.g., `-o` / `--output`, `-v` / `--verbose`, `-q` / `--quiet`).
- **Verbosity control**: default output is clean and informative. `-v` / `--verbose` adds operational detail. `-q` / `--quiet` suppresses all non-error output. These are mutually exclusive.
- **Exit codes**: 0 on success, 1 on user error (bad args, missing files), 2 on parse/data errors.
- **Progress feedback**: for long-running operations on large files, provide periodic progress indicators (record counts, elapsed time) at default verbosity. Suppressed by `--quiet`.

## Distribution & Build

- Standalone executables for **Windows (`.exe`)** and **Ubuntu (ELF binary)**.
- The executable must be fully self-contained — no assumption of a Python installation on the target system.
- Build and release scripts live in `scripts/`.

## Coding Conventions

- **No type stubs or heavy typing unless asked.** Light type hints on function signatures are fine.
- **Docstrings**: imperative mood, one-liner for simple functions. Numpy/Google-style only if the function is complex enough to warrant structured docs.
- **Error handling**: fail loud. `try/except` blocks must not swallow exceptions silently. Print or log the error context and re-raise or exit nonzero.
- **File I/O**: always specify `encoding='utf-8'` explicitly.
- **Naming**: snake_case everywhere. No Hungarian notation. Module names are short lowercase nouns or verb-noun pairs (`parser.py`, `analyze.py`, `export_csv.py`).
- **Project structure**: follow the `src/` layout. The importable package is `sms_backup_parser` under `src/sms_backup_parser/`. Do not put application code in the project root.
- **Tests**: `pytest`. Put tests in `tests/`. Mirror the source module name (`test_parser.py`). No test file without at least one assertion.
- **Avoid over-engineering.** Only make changes that are directly requested or clearly necessary. Do not add features, refactor code, or make improvements beyond what was asked.

## Changelog

Maintain `CHANGELOG.md` in [Keep a Changelog](https://keepachangelog.com/) format. Update it with every meaningful change — new features, bug fixes, schema changes, CLI interface changes, and non-trivial refactors. Do not log typo fixes, comment edits, or purely internal renames.

Every task that modifies behavior, output, or the public interface must include a corresponding `CHANGELOG.md` update.

## Data Sensitivity

Backup exports contain PII: phone numbers, contact names, message bodies, timestamps, and base64-encoded media. **Never commit sample data or real exports to version control.** Test fixtures must use synthetic/anonymized data.

The `./reference/SyncTech-docs/` and `./reference/SyncTech-utilities/` directories contain material not licensed for redistribution and must never be committed.

## License

This project is licensed under the **Apache License 2.0**.
