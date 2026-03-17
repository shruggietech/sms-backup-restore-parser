"""Progress reporting for long-running parse operations."""

import sys
import time


class ProgressTracker:
    """Track and report parsing progress to stderr.

    Verbosity levels:
        0 (quiet)   -- all output suppressed
        1 (normal)  -- periodic in-place progress updates every 10k records or 2s
        2 (verbose) -- per-record detail with type and address/number
    """

    REPORT_INTERVAL_RECORDS = 10_000
    REPORT_INTERVAL_SECONDS = 2.0

    def __init__(self, verbosity=1, stream=None):
        self._verbosity = verbosity
        self._stream = stream or sys.stderr
        self._counts = {"sms": 0, "mms": 0, "call": 0}
        self._start_time = None
        self._last_report_time = 0.0
        self._last_report_total = 0

    @property
    def counts(self):
        """Return a copy of current record counts."""
        return dict(self._counts)

    @property
    def total(self):
        return sum(self._counts.values())

    def _elapsed(self):
        if self._start_time is None:
            return 0.0
        return time.monotonic() - self._start_time

    def _should_report(self):
        total = self.total
        since_last = total - self._last_report_total
        elapsed_since = time.monotonic() - self._last_report_time
        return (since_last >= self.REPORT_INTERVAL_RECORDS
                or elapsed_since >= self.REPORT_INTERVAL_SECONDS)

    def _print_progress(self):
        elapsed = self._elapsed()
        parts = []
        for rtype in ("sms", "mms", "call"):
            count = self._counts[rtype]
            if count > 0:
                parts.append(f"{count:,} {rtype}")
        summary = " | ".join(parts) if parts else "0 records"
        self._stream.write(f"\r  Parsed: {summary}  [{elapsed:.1f}s]")
        self._stream.flush()
        self._last_report_time = time.monotonic()
        self._last_report_total = self.total

    def start(self):
        """Mark the beginning of a parse operation."""
        self._start_time = time.monotonic()
        self._last_report_time = self._start_time

    def update(self, record_type):
        """Increment counter for record_type and print progress if due."""
        self._counts[record_type] = self._counts.get(record_type, 0) + 1
        if self._verbosity >= 1 and self._should_report():
            self._print_progress()

    def update_verbose(self, record_type, record):
        """At verbose level, print per-record detail after updating."""
        self.update(record_type)
        if self._verbosity >= 2:
            ident = ""
            if record_type == "call":
                ident = record.get("number", "?")
            elif record_type in ("sms", "mms"):
                ident = record.get("address", "?")
            self._stream.write(
                f"\r  [{self.total:,}] {record_type}: {ident}\n"
            )
            self._stream.flush()

    def finish(self):
        """Print final summary line."""
        if self._verbosity < 1:
            return
        elapsed = self._elapsed()
        # Clear the in-place progress line
        self._stream.write("\r" + " " * 80 + "\r")
        parts = []
        for rtype, label in (("sms", "SMS"), ("mms", "MMS"), ("call", "calls")):
            count = self._counts[rtype]
            if count > 0:
                parts.append(f"{count:,} {label}")
        if parts:
            summary = ", ".join(parts)
        else:
            summary = "0 records"
        self._stream.write(f"  Parsed {summary} in {elapsed:.1f}s\n")
        self._stream.flush()
