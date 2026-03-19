# SMS Backup & Restore Parser

[![Python 3.12+](https://img.shields.io/badge/python-3.12%2B-blue?logo=python&logoColor=white)](https://www.python.org/downloads/)
[![License: Apache 2.0](https://img.shields.io/badge/license-Apache%202.0-green?logo=apache)](LICENSE)
[![Version](https://img.shields.io/badge/version-0.1.3-orange)](CHANGELOG.md)
[![Documentation](https://img.shields.io/github/actions/workflow/status/shruggietech/sms-backup-restore-parser/docs.yml?label=docs&logo=materialformkdocs&logoColor=white)](https://shruggietech.github.io/sms-backup-restore-parser/)
[![Code Style: Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff)

CLI utility for parsing [SyncTech SMS Backup & Restore](https://www.synctech.com.au/sms-backup-restore/) XML exports into structured JSON and generating analytical reports.

## Features

- **Streaming XML parse** -- handles multi-gigabyte backup files without loading the full DOM into memory
- **Structured JSON output** -- SMS, MMS, and call log records converted to schema-validated JSON
- **Built-in reports** -- summary statistics, per-contact breakdowns, and timeline views
- **Media stripping** -- omit base64-encoded MMS media for smaller analytical exports
- **Standalone executables** -- pre-built binaries for Windows and Ubuntu (no Python required)

## Quick Start

### Install from source

```bash
python -m venv .venv
source .venv/bin/activate   # .venv\Scripts\activate on Windows
pip install -e .
```

### Parse a backup

```bash
sms-backup-parser parse sms-backup.xml -o ./output
```

### Generate a report

```bash
sms-backup-parser report output/sms-backup_sms.json -t summary
```

## CLI Usage

The tool provides two main subcommands:

### `parse` -- Convert XML to JSON

```bash
# Basic parse
sms-backup-parser parse backup.xml

# Parse multiple files, strip media, compact output
sms-backup-parser parse *.xml -o ./output --strip-media --compact

# Single combined output file instead of per-type files
sms-backup-parser parse backup.xml --combined
```

### `report` -- Generate analytical reports

```bash
# Summary statistics
sms-backup-parser report backup_sms.json -t summary

# Top 50 contacts by volume, CSV format
sms-backup-parser report *.json -t contacts --top-n 50 --format csv

# All report types to a file
sms-backup-parser report backup.json -t all -o report.txt
```

### Global flags

| Flag | Description |
|------|-------------|
| `-v` / `--verbose` | Show operational detail (file paths, record counts, timing) |
| `-q` / `--quiet` | Suppress all non-error output |
| `version` | Print version number and exit |

Run `sms-backup-parser --help` or `sms-backup-parser <command> --help` for full details.

## Documentation

Full documentation is available in the [docs/](docs/) directory, including:

- [Installation Guide](docs/installation.md)
- [CLI Usage](docs/usage.md)
- [JSON Schema Reference](docs/schema.md)
- [Report Types](docs/reports.md)

## License

[Apache License 2.0](LICENSE)
