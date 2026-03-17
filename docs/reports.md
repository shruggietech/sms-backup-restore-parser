# Report Types

Reports are generated from JSON files produced by the `parse` command. Use the `report` subcommand to generate them:

```bash
sms-backup-parser report <input.json> -t <type> [--format <format>] [-o <file>]
```

Available output formats: `text` (default), `csv`, `json`.

## Summary Report

**Type flag:** `-t summary`

Provides aggregate statistics across all records in the input files.

**Includes:**

- Total counts by record type (SMS, MMS, calls)
- Date range (earliest and latest record)
- Breakdown by direction (sent vs. received for messages, incoming vs. outgoing vs. missed for calls)
- Message read/unread counts
- MMS media vs. text-only counts

**Example (text format):**

```
=== SMS Backup Summary ===

SMS Messages:     12,847
  Received:        7,231
  Sent:            5,616
  Unread:             14

MMS Messages:      1,923
  Received:        1,104
  Sent:              819
  Text-only:         342
  With media:      1,581

Calls:             8,412
  Incoming:        3,891
  Outgoing:        2,734
  Missed:          1,787

Date range: 2019-03-14 to 2024-12-31
```

## Contacts Report

**Type flag:** `-t contacts`

Ranks contacts by message and call volume. The number of entries shown is controlled by `--top-n` (default: 20).

**Includes:**

- Contact name and phone number
- Total messages (SMS + MMS) sent and received
- Total calls (incoming, outgoing, missed)
- Total call duration

**Example (text format):**

```
=== Top 20 Contacts by Volume ===

 #  Contact              Messages  Calls  Call Duration
 1  Alice Smith              2,341    487  12h 34m
 2  Bob Jones                1,876    312   8h 12m
 3  Carol Williams           1,203    198   5h 47m
...
```

**CSV format** produces a flat table suitable for spreadsheet import with columns: `rank`, `contact_name`, `address`, `sms_received`, `sms_sent`, `mms_received`, `mms_sent`, `calls_incoming`, `calls_outgoing`, `calls_missed`, `call_duration_seconds`.

## Timeline Report

**Type flag:** `-t timeline`

Shows message and call activity over time, aggregated by day, week, or month.

**Includes:**

- Period label (date or date range)
- SMS count per period
- MMS count per period
- Call count per period
- Total activity per period

**Example (text format):**

```
=== Activity Timeline (Monthly) ===

Period          SMS    MMS  Calls  Total
2024-01         892    143    621  1,656
2024-02         734    118    589  1,441
2024-03       1,021    167    702  1,890
2024-04         687    102    534  1,323
...
```

**JSON format** produces an array of period objects for downstream visualization or analysis.

## Generating All Reports

Use `-t all` to run every report type in sequence:

```bash
sms-backup-parser report backup.json -t all -o full-report.txt
```

Each report section is separated by a blank line with a header.

## Output Formats

| Format | Flag | Description |
|--------|------|-------------|
| Text | `--format text` | Human-readable plain text (default) |
| CSV | `--format csv` | Comma-separated values for spreadsheet import |
| JSON | `--format json` | Structured JSON for programmatic consumption |
