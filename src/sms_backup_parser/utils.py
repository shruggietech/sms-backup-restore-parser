"""Shared utility functions."""

from datetime import datetime, timezone


def java_epoch_to_iso(ms_str):
    """Convert Java epoch milliseconds string to ISO 8601 UTC string.

    Returns None if the input is missing, non-numeric, or not a reasonable timestamp.
    """
    if not ms_str or not ms_str.isdigit():
        return None
    ms = int(ms_str)
    if ms <= 0:
        return None
    try:
        return datetime.fromtimestamp(ms / 1000.0, tz=timezone.utc).isoformat()
    except (OSError, OverflowError, ValueError):
        return None


def format_file_size(size_bytes):
    """Format byte count as human-readable string."""
    for unit in ('B', 'KB', 'MB', 'GB'):
        if abs(size_bytes) < 1024.0:
            return f"{size_bytes:.1f} {unit}"
        size_bytes /= 1024.0
    return f"{size_bytes:.1f} TB"
