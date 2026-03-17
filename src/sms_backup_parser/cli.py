"""Command-line interface for sms-backup-parser."""

import argparse
import sys
from pathlib import Path

from . import __version__


def build_parser():
    """Construct the top-level argument parser with all subcommands."""
    parser = argparse.ArgumentParser(
        prog="sms-backup-parser",
        description=(
            "Parse SyncTech SMS Backup & Restore XML exports into structured "
            "JSON and generate analytical reports."
        ),
        epilog=(
            "Exit codes: 0 = success, 1 = user error (bad args, missing files), "
            "2 = parse/data error"
        ),
    )

    # Top-level mutually exclusive verbosity flags
    verbosity = parser.add_mutually_exclusive_group()
    verbosity.add_argument(
        "-v", "--verbose",
        action="store_true",
        default=False,
        help=(
            "Increase output verbosity. Shows per-record detail during parsing, "
            "file paths as they are opened, and extended timing information."
        ),
    )
    verbosity.add_argument(
        "-q", "--quiet",
        action="store_true",
        default=False,
        help=(
            "Suppress all non-error output. Only fatal errors are printed to "
            "stderr. Useful for scripted pipelines where only the exit code matters."
        ),
    )

    subparsers = parser.add_subparsers(
        dest="command",
        title="commands",
        description="Available commands (use '<command> --help' for details)",
    )

    # ── parse subcommand ────────────────────────────────────────────────
    parse_parser = subparsers.add_parser(
        "parse",
        help="Parse XML backup files into structured JSON",
        description=(
            "Parse one or more SyncTech SMS Backup & Restore XML exports into "
            "structured JSON files. Supports SMS, MMS, and call log exports. "
            "By default, produces separate JSON files per record type (SMS, MMS, "
            "calls). Use --combined for a single merged output file."
        ),
        epilog=(
            "Examples:\n"
            "  sms-backup-parser parse sms-20240101.xml\n"
            "  sms-backup-parser parse *.xml -o ./output --strip-media\n"
            "  sms-backup-parser parse backup.xml --combined --compact\n"
        ),
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parse_parser.add_argument(
        "input",
        nargs="+",
        help=(
            "One or more XML backup files to parse (supports SMS, MMS, and "
            "call log exports from SyncTech SMS Backup & Restore)"
        ),
    )
    parse_parser.add_argument(
        "-o", "--output-dir",
        default=None,
        metavar="DIR",
        help=(
            "Directory to write output JSON files into. Created automatically "
            "if it does not exist. Defaults to the same directory as each "
            "input file."
        ),
    )
    parse_parser.add_argument(
        "--combined",
        action="store_true",
        default=False,
        help=(
            "Write a single combined JSON file per input instead of separate "
            "per-type files. The combined file contains top-level 'sms', 'mms', "
            "and 'calls' arrays."
        ),
    )
    parse_parser.add_argument(
        "--strip-media",
        action="store_true",
        default=False,
        help=(
            "Omit base64-encoded media data from MMS parts, significantly "
            "reducing output size for analytical use cases where media content "
            "is not needed"
        ),
    )
    parse_parser.add_argument(
        "--no-date-iso",
        action="store_true",
        default=False,
        help=(
            "Skip injection of computed 'date_iso' fields (ISO 8601, UTC) "
            "derived from the Java-epoch-millisecond 'date' attribute. By "
            "default, date_iso is added to every record for human readability "
            "and tooling interop."
        ),
    )
    parse_parser.add_argument(
        "--validate",
        action="store_true",
        default=False,
        help=(
            "Validate output JSON files against the project's JSON Schema "
            "after writing. Requires the jsonschema package: "
            "pip install sms-backup-restore-parser[validate]"
        ),
    )

    # Pretty vs compact output (mutually exclusive)
    format_group = parse_parser.add_mutually_exclusive_group()
    format_group.add_argument(
        "--pretty",
        action="store_true",
        default=True,
        help=(
            "Pretty-print JSON output with 2-space indentation (the default). "
            "Produces human-readable files at the cost of larger file size."
        ),
    )
    format_group.add_argument(
        "--compact",
        action="store_true",
        default=False,
        help=(
            "Write compact JSON with no indentation or extra whitespace. "
            "Produces smaller files suitable for machine consumption."
        ),
    )

    parse_parser.set_defaults(func=cmd_parse)

    # ── report subcommand ───────────────────────────────────────────────
    report_parser = subparsers.add_parser(
        "report",
        help="Generate analytical reports from parsed JSON",
        description=(
            "Generate human-readable analytical reports from previously parsed "
            "JSON files. Supports multiple report types including summary "
            "statistics, per-contact breakdowns, and timeline views."
        ),
        epilog=(
            "Examples:\n"
            "  sms-backup-parser report sms_sms.json\n"
            "  sms-backup-parser report *.json -t contacts --top-n 50\n"
            "  sms-backup-parser report backup.json -t all --format csv -o report.csv\n"
        ),
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    report_parser.add_argument(
        "input",
        nargs="+",
        help=(
            "One or more JSON files produced by the 'parse' command. Accepts "
            "both per-type files (e.g., backup_sms.json) and combined files."
        ),
    )
    report_parser.add_argument(
        "-t", "--type",
        choices=["summary", "contacts", "timeline", "all"],
        default="summary",
        help=(
            "Type of report to generate. 'summary' provides aggregate counts "
            "and date ranges. 'contacts' ranks contacts by message and call "
            "volume. 'timeline' shows activity over time. 'all' generates "
            "every available report type sequentially. (default: summary)"
        ),
    )
    report_parser.add_argument(
        "-o", "--output",
        default=None,
        metavar="FILE",
        help=(
            "File path to write the report to. Use '-' to explicitly write to "
            "stdout. If omitted, output is printed to stdout."
        ),
    )
    report_parser.add_argument(
        "--format",
        choices=["text", "csv", "json"],
        default="text",
        dest="output_format",
        help=(
            "Output format for the report. 'text' produces human-readable "
            "plain text, 'csv' produces comma-separated values suitable for "
            "spreadsheet import, 'json' produces structured JSON. "
            "(default: text)"
        ),
    )
    report_parser.add_argument(
        "--top-n",
        type=int,
        default=20,
        metavar="N",
        help=(
            "Number of entries to include in ranked reports such as 'contacts'. "
            "For example, --top-n 50 shows the top 50 contacts by volume. "
            "(default: 20)"
        ),
    )

    report_parser.set_defaults(func=cmd_report)

    # ── version subcommand ──────────────────────────────────────────────
    version_parser = subparsers.add_parser(
        "version",
        help="Print the version number and exit",
        description="Display the installed version of sms-backup-parser.",
    )
    version_parser.set_defaults(func=cmd_version)

    return parser


# ── Subcommand handlers ─────────────────────────────────────────────────


def cmd_parse(args):
    """Execute the 'parse' subcommand."""

    # Validate all input files exist before starting any work
    input_paths = []
    for raw_path in args.input:
        p = Path(raw_path)
        if not p.exists():
            print(f"Error: Input file not found: {p}", file=sys.stderr)
            return 1
        if not p.is_file():
            print(f"Error: Not a file: {p}", file=sys.stderr)
            return 1
        input_paths.append(p)

    # Determine verbosity level: 0=quiet, 1=normal, 2=verbose
    if args.quiet:
        verbosity = 0
    elif args.verbose:
        verbosity = 2
    else:
        verbosity = 1

    # Determine JSON indentation
    indent = None if args.compact else 2

    inject_date_iso = not args.no_date_iso

    total_counts = {"sms": 0, "mms": 0, "call": 0}
    all_output_files = []

    if args.combined and len(input_paths) > 1:
        # Multi-file combined: merge all inputs into one output
        from .parser import parse_backup_multi
        from .progress import ProgressTracker

        output_dir = args.output_dir or str(input_paths[0].parent)

        def tracker_factory():
            return ProgressTracker(verbosity=verbosity)

        if verbosity >= 1:
            print(f"Parsing {len(input_paths)} files into combined output...",
                  file=sys.stderr)

        result = parse_backup_multi(
            input_paths=input_paths,
            output_dir=output_dir,
            strip_media=args.strip_media,
            inject_date_iso=inject_date_iso,
            indent=indent,
            progress_tracker_factory=tracker_factory,
        )

        total_counts["sms"] = result["sms_count"]
        total_counts["mms"] = result["mms_count"]
        total_counts["call"] = result["call_count"]
        all_output_files.extend(result["output_files"])

        if verbosity >= 2:
            for f in result["output_files"]:
                print(f"  Wrote: {f}", file=sys.stderr)
    else:
        # Single file (combined or separate) or multi-file separate
        from .parser import parse_backup
        from .progress import ProgressTracker

        for input_path in input_paths:
            if verbosity >= 1:
                print(f"Parsing {input_path}...", file=sys.stderr)

            tracker = ProgressTracker(verbosity=verbosity)

            result = parse_backup(
                input_path=input_path,
                output_dir=args.output_dir,
                combined=args.combined,
                strip_media=args.strip_media,
                inject_date_iso=inject_date_iso,
                indent=indent,
                progress_tracker=tracker,
            )

            total_counts["sms"] += result["sms_count"]
            total_counts["mms"] += result["mms_count"]
            total_counts["call"] += result["call_count"]
            all_output_files.extend(result["output_files"])

            if verbosity >= 2:
                for f in result["output_files"]:
                    print(f"  Wrote: {f}", file=sys.stderr)

    # Schema validation pass
    if args.validate:
        from .validate import validate_output as _validate

        if verbosity >= 1:
            print("Validating output...", file=sys.stderr)

        for output_file in all_output_files:
            try:
                _validate(output_file)
                if verbosity >= 1:
                    print(f"  OK: {output_file}", file=sys.stderr)
            except ImportError as e:
                print(f"Error: {e}", file=sys.stderr)
                return 1
            except Exception as e:
                print(f"Validation failed for {output_file}: {e}", file=sys.stderr)
                return 2

    # Print final summary
    if verbosity >= 1 and len(input_paths) > 1:
        parts = []
        for rtype, label in (("sms", "SMS"), ("mms", "MMS"), ("call", "calls")):
            if total_counts[rtype] > 0:
                parts.append(f"{total_counts[rtype]:,} {label}")
        summary = ", ".join(parts) if parts else "0 records"
        print(
            f"Total across {len(input_paths)} files: {summary}",
            file=sys.stderr,
        )

    return 0


def cmd_report(args):
    """Execute the 'report' subcommand."""
    # Validate all input files exist
    input_paths = []
    for raw_path in args.input:
        p = Path(raw_path)
        if not p.exists():
            print(f"Error: Input file not found: {p}", file=sys.stderr)
            return 1
        if not p.is_file():
            print(f"Error: Not a file: {p}", file=sys.stderr)
            return 1
        input_paths.append(p)

    try:
        from . import reports
    except ImportError:
        print(
            "Error: Reports module not yet implemented.",
            file=sys.stderr,
        )
        return 2

    # Determine output destination
    if args.output is None or args.output == "-":
        output_file = sys.stdout
        should_close = False
    else:
        output_path = Path(args.output)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_file = open(output_path, 'w', encoding='utf-8')
        should_close = True

    try:
        data = reports.load_report_data(input_paths)
        result = reports.generate_report(
            data,
            report_type=args.type,
            output_format=args.output_format,
            top_n=args.top_n,
        )
        output_file.write(result)
        if not result.endswith('\n'):
            output_file.write('\n')
        return 0
    finally:
        if should_close:
            output_file.close()


def cmd_version(args):
    """Execute the 'version' subcommand."""
    print(f"sms-backup-parser {__version__}")
    return 0


# ── Entry point ─────────────────────────────────────────────────────────


def main(argv=None):
    """Entry point for the CLI."""
    parser = build_parser()
    args = parser.parse_args(argv)

    if not hasattr(args, "func"):
        parser.print_help()
        return 0

    try:
        return args.func(args)
    except FileNotFoundError as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1
    except PermissionError as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1
    except KeyboardInterrupt:
        print("\nInterrupted.", file=sys.stderr)
        return 1
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    sys.exit(main())
