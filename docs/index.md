# SMS Backup & Restore Parser

A CLI utility for parsing [SyncTech SMS Backup & Restore](https://www.synctech.com.au/sms-backup-restore/) XML exports into structured JSON and generating analytical reports.

## What It Does

SyncTech's SMS Backup & Restore app produces XML backup files containing SMS messages, MMS messages (with embedded media), and call logs. This tool converts those XML files into clean, schema-validated JSON suitable for analysis with tools like DuckDB, jq, or custom scripts.

It also generates built-in analytical reports -- summary statistics, per-contact breakdowns, and timeline views -- directly from the parsed data.

## Key Capabilities

- **Streaming parse** -- processes multi-gigabyte XML exports with constant memory usage via `iterparse`
- **Schema-validated JSON** -- output conforms to a JSON Schema (draft-07) that documents every field and enum value
- **Computed fields** -- injects ISO 8601 timestamps (`date_iso`) from Java-epoch-millisecond values for human readability
- **Media stripping** -- optionally omit base64-encoded MMS media to produce compact analytical exports
- **Multiple report types** -- summary, contacts, and timeline reports in text, CSV, or JSON format
- **Standalone binaries** -- distributed as self-contained executables for Windows and Ubuntu

## Documentation

- [Installation](installation.md) -- download binaries, install from source, or set up a development environment
- [Usage](usage.md) -- complete CLI reference with flags, examples, and common workflows
- [Schema Reference](schema.md) -- field-by-field documentation of the JSON output format
- [Reports](reports.md) -- description of each report type with example output
