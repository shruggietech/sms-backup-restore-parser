# CLI Usage

## Global Options

These flags apply to all subcommands and must appear before the subcommand name:

| Flag | Description |
|------|-------------|
| `-v` / `--verbose` | Increase output verbosity. Shows file paths, per-record detail, and extended timing. |
| `-q` / `--quiet` | Suppress all non-error output. Only fatal errors are printed to stderr. |

These are mutually exclusive -- you cannot combine `-v` and `-q`.

```bash
sms-backup-parser -v parse backup.xml
sms-backup-parser -q parse backup.xml
```

## `parse` -- Convert XML to JSON

Parse one or more SyncTech SMS Backup & Restore XML exports into structured JSON files.

```
sms-backup-parser parse [options] <input> [<input> ...]
```

### Arguments

| Argument | Description |
|----------|-------------|
| `input` | One or more XML backup files (SMS, MMS, or call log exports) |

### Options

| Flag | Default | Description |
|------|---------|-------------|
| `-o` / `--output-dir DIR` | Same directory as input | Directory for output JSON files (created if missing) |
| `--combined` | Off | Write a single JSON file with top-level `sms`, `mms`, and `calls` arrays instead of separate per-type files |
| `--strip-media` | Off | Omit base64-encoded media data from MMS parts, significantly reducing output size |
| `--no-date-iso` | Off | Skip injection of computed `date_iso` fields (ISO 8601, UTC) |
| `--validate` | Off | Validate output against the JSON Schema after writing (requires `[validate]` extra) |
| `--pretty` | On | Pretty-print JSON with 2-space indentation |
| `--compact` | Off | Write compact JSON with no whitespace (mutually exclusive with `--pretty`) |

### Examples

```bash
# Parse a single backup file
sms-backup-parser parse sms-20240101.xml

# Parse multiple files into a specific output directory
sms-backup-parser parse *.xml -o ./output

# Compact output without media for analysis
sms-backup-parser parse backup.xml --strip-media --compact -o ./output

# Single combined file with schema validation
sms-backup-parser parse backup.xml --combined --validate
```

### Output Files

By default, the parser writes separate JSON files per record type found in the input:

- `<input>_sms.json` -- SMS messages
- `<input>_mms.json` -- MMS messages
- `<input>_calls.json` -- call log entries

With `--combined`, a single `<input>.json` file is written containing all record types.

## `report` -- Generate Analytical Reports

Generate human-readable reports from previously parsed JSON files.

```
sms-backup-parser report [options] <input> [<input> ...]
```

### Arguments

| Argument | Description |
|----------|-------------|
| `input` | One or more JSON files produced by the `parse` command |

### Options

| Flag | Default | Description |
|------|---------|-------------|
| `-t` / `--type TYPE` | `summary` | Report type: `summary`, `contacts`, `timeline`, or `all` |
| `-o` / `--output FILE` | stdout | File path to write the report (use `-` for stdout) |
| `--format FORMAT` | `text` | Output format: `text`, `csv`, or `json` |
| `--top-n N` | `20` | Number of entries in ranked reports (e.g., top contacts) |

### Examples

```bash
# Default summary report to stdout
sms-backup-parser report backup_sms.json

# Top 50 contacts in CSV format
sms-backup-parser report *.json -t contacts --top-n 50 --format csv

# All report types written to a file
sms-backup-parser report backup.json -t all -o report.txt

# Timeline report as JSON
sms-backup-parser report backup_sms.json -t timeline --format json -o timeline.json
```

## `version` -- Print Version

```bash
sms-backup-parser version
```

## Exit Codes

| Code | Meaning |
|------|---------|
| `0` | Success |
| `1` | User error (bad arguments, missing files, missing dependencies) |
| `2` | Parse or data error (malformed XML, validation failure) |

## Common Workflows

### Parse and summarize

```bash
sms-backup-parser parse backup.xml -o ./output
sms-backup-parser report ./output/backup_sms.json -t summary
```

### Compact analytical export (no media)

```bash
sms-backup-parser parse backup.xml --strip-media --compact -o ./output
```

This produces much smaller JSON files suitable for loading into DuckDB, jq, or Python scripts.

### Ad hoc inspection with jq

```bash
# Count SMS messages per contact
jq '[.sms[] | .contact_name] | group_by(.) | map({name: .[0], count: length}) | sort_by(-.count)' output/backup_sms.json

# List all MMS media types
jq '[.mms[].parts[]?.ct] | unique' output/backup_mms.json
```

### Validate output against schema

```bash
pip install -e ".[validate]"
sms-backup-parser parse backup.xml --validate
```
