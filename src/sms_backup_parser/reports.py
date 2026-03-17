"""Report generation for parsed SMS Backup & Restore data."""

import csv
import io
import json
import os
from collections import defaultdict

from . import models


def load_report_data(json_paths):
    """Load and merge data from one or more JSON files.

    Handles both per-type files (bare arrays) and combined files
    (object with sms/mms/calls keys).
    Returns dict with keys 'sms', 'mms', 'calls', each a list.
    """
    merged = {"sms": [], "mms": [], "calls": []}

    for path in json_paths:
        with open(path, encoding="utf-8") as f:
            raw = json.load(f)

        if isinstance(raw, dict):
            for key in ("sms", "mms", "calls"):
                if key in raw and isinstance(raw[key], list):
                    merged[key].extend(raw[key])
        elif isinstance(raw, list):
            record_type = _infer_type_from_path(path)
            if record_type is None:
                record_type = _infer_type_from_records(raw)
            if record_type:
                merged[record_type].extend(raw)
        # Silently skip unrecognized structures

    return merged


def _infer_type_from_path(path):
    """Guess record type from filename keywords."""
    basename = os.path.basename(path).lower()
    if "_sms" in basename:
        return "sms"
    if "_mms" in basename:
        return "mms"
    if "_calls" in basename or "_call" in basename:
        return "calls"
    return None


def _infer_type_from_records(records):
    """Guess record type by inspecting the first record's keys."""
    if not records:
        return None
    first = records[0]
    if not isinstance(first, dict):
        return None
    if "parts" in first:
        return "mms"
    if "duration" in first:
        return "calls"
    if "body" in first:
        return "sms"
    return None


# ---------------------------------------------------------------------------
# Formatting helpers
# ---------------------------------------------------------------------------

def _format_duration(total_seconds):
    """Format an integer number of seconds as HH:MM:SS."""
    total_seconds = int(total_seconds)
    hours, remainder = divmod(total_seconds, 3600)
    minutes, seconds = divmod(remainder, 60)
    return f"{hours}:{minutes:02d}:{seconds:02d}"


def _extract_dates(data):
    """Collect all date_iso values across record types, skipping missing ones."""
    dates = []
    for key in ("sms", "mms", "calls"):
        for rec in data.get(key, []):
            d = rec.get("date_iso")
            if d:
                dates.append(d)
    return dates


def _contact_key(record, record_type):
    """Return the contact address/number from a record."""
    if record_type == "sms":
        return record.get("address", "")
    elif record_type == "mms":
        return record.get("address", "") or _mms_primary_address(record)
    elif record_type == "calls":
        return record.get("number", "")
    return ""


def _mms_primary_address(record):
    """Extract the primary address from an MMS record's addr list."""
    addrs = record.get("addrs", [])
    for a in addrs:
        if a.get("type") == "137":  # From
            return a.get("address", "")
    for a in addrs:
        if a.get("type") == "151":  # To
            return a.get("address", "")
    if addrs:
        return addrs[0].get("address", "")
    return ""


def _contact_name(record, record_type):
    """Return the contact name from a record, or empty string."""
    if record_type in ("sms", "calls"):
        return record.get("contact_name", "")
    elif record_type == "mms":
        return record.get("contact_name", "")
    return ""


# ---------------------------------------------------------------------------
# 1. Summary Report
# ---------------------------------------------------------------------------

def generate_summary(data, output_format="text"):
    """Generate a summary report of the backup data."""
    sms_list = data.get("sms", [])
    mms_list = data.get("mms", [])
    calls_list = data.get("calls", [])

    sms_count = len(sms_list)
    mms_count = len(mms_list)
    calls_count = len(calls_list)

    # Date range
    dates = _extract_dates(data)
    earliest = min(dates) if dates else None
    latest = max(dates) if dates else None

    # SMS by type
    sms_by_type = defaultdict(int)
    for rec in sms_list:
        type_code = str(rec.get("type", ""))
        label = models.SMS_TYPES.get(type_code, f"Unknown ({type_code})")
        sms_by_type[label] += 1

    # Calls by type
    calls_by_type = defaultdict(int)
    for rec in calls_list:
        type_code = str(rec.get("type", ""))
        label = models.CALL_TYPES.get(type_code, f"Unknown ({type_code})")
        calls_by_type[label] += 1

    # Total call duration
    total_call_seconds = 0
    for rec in calls_list:
        dur = rec.get("duration", 0)
        try:
            total_call_seconds += int(dur)
        except (ValueError, TypeError):
            pass

    # Unique contacts
    contacts = set()
    for rec in sms_list:
        addr = rec.get("address", "")
        if addr:
            contacts.add(addr)
    for rec in mms_list:
        addr = _contact_key(rec, "mms")
        if addr:
            contacts.add(addr)
    for rec in calls_list:
        num = rec.get("number", "")
        if num:
            contacts.add(num)

    # MMS with media
    mms_with_media = sum(1 for rec in mms_list if rec.get("text_only") != "1")

    summary = {
        "sms_count": sms_count,
        "mms_count": mms_count,
        "calls_count": calls_count,
        "earliest_date": earliest,
        "latest_date": latest,
        "sms_by_type": dict(sms_by_type),
        "calls_by_type": dict(calls_by_type),
        "total_call_duration_seconds": total_call_seconds,
        "total_call_duration": _format_duration(total_call_seconds),
        "unique_contacts": len(contacts),
        "mms_with_media": mms_with_media,
    }

    if output_format == "json":
        return json.dumps(summary, indent=2, ensure_ascii=False)
    elif output_format == "csv":
        return _summary_to_csv(summary)
    else:
        return _summary_to_text(summary)


def _summary_to_text(s):
    """Render summary dict as human-readable text."""
    lines = []
    lines.append("=== Backup Summary ===")
    lines.append("")
    lines.append("Records")
    lines.append(f"  SMS:   {s['sms_count']:>8,}")
    lines.append(f"  MMS:   {s['mms_count']:>8,}")
    lines.append(f"  Calls: {s['calls_count']:>8,}")
    lines.append("")
    lines.append("Date Range")
    lines.append(f"  Earliest: {s['earliest_date'] or 'N/A'}")
    lines.append(f"  Latest:   {s['latest_date'] or 'N/A'}")
    lines.append("")

    if s["sms_by_type"]:
        lines.append("SMS by Type")
        for label, count in sorted(s["sms_by_type"].items()):
            lines.append(f"  {label + ':':.<16}{count:>8,}")
        lines.append("")

    if s["calls_by_type"]:
        lines.append("Calls by Type")
        for label, count in sorted(s["calls_by_type"].items()):
            lines.append(f"  {label + ':':.<16}{count:>8,}")
        lines.append("")

    lines.append(f"Total Call Duration: {s['total_call_duration']}")
    lines.append(f"Unique Contacts: {s['unique_contacts']:,}")
    lines.append(f"MMS with Media: {s['mms_with_media']:,}")
    return "\n".join(lines)


def _summary_to_csv(s):
    """Render summary dict as key,value CSV."""
    buf = io.StringIO()
    writer = csv.writer(buf)
    writer.writerow(["key", "value"])
    writer.writerow(["sms_count", s["sms_count"]])
    writer.writerow(["mms_count", s["mms_count"]])
    writer.writerow(["calls_count", s["calls_count"]])
    writer.writerow(["earliest_date", s["earliest_date"] or ""])
    writer.writerow(["latest_date", s["latest_date"] or ""])
    for label, count in sorted(s["sms_by_type"].items()):
        writer.writerow([f"sms_type_{label.lower()}", count])
    for label, count in sorted(s["calls_by_type"].items()):
        writer.writerow([f"call_type_{label.lower()}", count])
    writer.writerow(["total_call_duration_seconds", s["total_call_duration_seconds"]])
    writer.writerow(["total_call_duration", s["total_call_duration"]])
    writer.writerow(["unique_contacts", s["unique_contacts"]])
    writer.writerow(["mms_with_media", s["mms_with_media"]])
    return buf.getvalue()


# ---------------------------------------------------------------------------
# 2. Contacts Report
# ---------------------------------------------------------------------------

def generate_contacts(data, output_format="text", top_n=20):
    """Generate a per-contact activity report."""
    contacts = defaultdict(lambda: {
        "name": "(Unknown)",
        "sms_received": 0,
        "sms_sent": 0,
        "mms_received": 0,
        "mms_sent": 0,
        "calls_incoming": 0,
        "calls_outgoing": 0,
        "calls_missed": 0,
        "call_duration": 0,
        "first_date": None,
        "last_date": None,
    })

    def _update_dates(entry, date_iso):
        if not date_iso:
            return
        if entry["first_date"] is None or date_iso < entry["first_date"]:
            entry["first_date"] = date_iso
        if entry["last_date"] is None or date_iso > entry["last_date"]:
            entry["last_date"] = date_iso

    # SMS
    for rec in data.get("sms", []):
        addr = rec.get("address", "")
        if not addr:
            continue
        entry = contacts[addr]
        name = rec.get("contact_name", "")
        if name and entry["name"] == "(Unknown)":
            entry["name"] = name
        type_code = str(rec.get("type", ""))
        if type_code == "1":
            entry["sms_received"] += 1
        elif type_code == "2":
            entry["sms_sent"] += 1
        _update_dates(entry, rec.get("date_iso"))

    # MMS
    for rec in data.get("mms", []):
        addr = _contact_key(rec, "mms")
        if not addr:
            continue
        entry = contacts[addr]
        name = rec.get("contact_name", "")
        if name and entry["name"] == "(Unknown)":
            entry["name"] = name
        msg_box = str(rec.get("msg_box", ""))
        if msg_box == "1":
            entry["mms_received"] += 1
        elif msg_box == "2":
            entry["mms_sent"] += 1
        _update_dates(entry, rec.get("date_iso"))

    # Calls
    for rec in data.get("calls", []):
        num = rec.get("number", "")
        if not num:
            continue
        entry = contacts[num]
        name = rec.get("contact_name", "")
        if name and entry["name"] == "(Unknown)":
            entry["name"] = name
        type_code = str(rec.get("type", ""))
        if type_code == "1":
            entry["calls_incoming"] += 1
        elif type_code == "2":
            entry["calls_outgoing"] += 1
        elif type_code == "3":
            entry["calls_missed"] += 1
        try:
            entry["call_duration"] += int(rec.get("duration", 0))
        except (ValueError, TypeError):
            pass
        _update_dates(entry, rec.get("date_iso"))

    if not contacts:
        if output_format == "json":
            return "[]"
        elif output_format == "csv":
            return "No contact data available.\n"
        else:
            return "=== Contacts Report ===\n\nNo contact data available."

    # Sort by total activity descending
    def _total_activity(item):
        _, e = item
        return (
            e["sms_received"] + e["sms_sent"]
            + e["mms_received"] + e["mms_sent"]
            + e["calls_incoming"] + e["calls_outgoing"] + e["calls_missed"]
        )

    sorted_contacts = sorted(contacts.items(), key=_total_activity, reverse=True)[:top_n]

    rows = []
    for addr, e in sorted_contacts:
        rows.append({
            "contact": addr,
            "name": e["name"],
            "sms_received": e["sms_received"],
            "sms_sent": e["sms_sent"],
            "mms_received": e["mms_received"],
            "mms_sent": e["mms_sent"],
            "calls_incoming": e["calls_incoming"],
            "calls_outgoing": e["calls_outgoing"],
            "calls_missed": e["calls_missed"],
            "call_duration": _format_duration(e["call_duration"]),
            "call_duration_seconds": e["call_duration"],
            "first_date": e["first_date"] or "N/A",
            "last_date": e["last_date"] or "N/A",
        })

    if output_format == "json":
        return json.dumps(rows, indent=2, ensure_ascii=False)
    elif output_format == "csv":
        return _contacts_to_csv(rows)
    else:
        return _contacts_to_text(rows)


def _contacts_to_text(rows):
    """Render contacts as a fixed-width table."""
    lines = []
    lines.append("=== Contacts Report ===")
    lines.append("")

    # Column headers
    header = (
        f"{'Contact':<20} {'Name':<16} "
        f"{'SMS(R/S)':>9} {'MMS(R/S)':>9} "
        f"{'Calls(In/Out/Miss)':>19} "
        f"{'Call Dur':>10} "
        f"{'First':>12} {'Last':>12}"
    )
    lines.append(header)
    lines.append("-" * len(header))

    for r in rows:
        contact = r["contact"][:19]
        name = r["name"][:15]
        sms = f"{r['sms_received']}/{r['sms_sent']}"
        mms = f"{r['mms_received']}/{r['mms_sent']}"
        calls = f"{r['calls_incoming']}/{r['calls_outgoing']}/{r['calls_missed']}"
        first = r["first_date"][:10] if r["first_date"] != "N/A" else "N/A"
        last = r["last_date"][:10] if r["last_date"] != "N/A" else "N/A"
        lines.append(
            f"{contact:<20} {name:<16} "
            f"{sms:>9} {mms:>9} "
            f"{calls:>19} "
            f"{r['call_duration']:>10} "
            f"{first:>12} {last:>12}"
        )

    return "\n".join(lines)


def _contacts_to_csv(rows):
    """Render contacts as CSV."""
    buf = io.StringIO()
    fieldnames = [
        "contact", "name",
        "sms_received", "sms_sent",
        "mms_received", "mms_sent",
        "calls_incoming", "calls_outgoing", "calls_missed",
        "call_duration", "call_duration_seconds",
        "first_date", "last_date",
    ]
    writer = csv.DictWriter(buf, fieldnames=fieldnames)
    writer.writeheader()
    for r in rows:
        writer.writerow(r)
    return buf.getvalue()


# ---------------------------------------------------------------------------
# 3. Timeline Report
# ---------------------------------------------------------------------------

def generate_timeline(data, output_format="text"):
    """Generate a daily activity timeline."""
    days = defaultdict(lambda: {
        "sms": 0,
        "mms": 0,
        "calls": 0,
        "call_duration": 0,
    })

    for rec in data.get("sms", []):
        d = rec.get("date_iso")
        if not d:
            continue
        day = d[:10]
        days[day]["sms"] += 1

    for rec in data.get("mms", []):
        d = rec.get("date_iso")
        if not d:
            continue
        day = d[:10]
        days[day]["mms"] += 1

    for rec in data.get("calls", []):
        d = rec.get("date_iso")
        if not d:
            continue
        day = d[:10]
        days[day]["calls"] += 1
        try:
            days[day]["call_duration"] += int(rec.get("duration", 0))
        except (ValueError, TypeError):
            pass

    if not days:
        if output_format == "json":
            return "[]"
        elif output_format == "csv":
            return "No timeline data available.\n"
        else:
            return "=== Timeline Report ===\n\nNo timeline data available."

    sorted_days = sorted(days.items())

    rows = []
    for day, counts in sorted_days:
        rows.append({
            "date": day,
            "sms": counts["sms"],
            "mms": counts["mms"],
            "calls": counts["calls"],
            "call_duration": _format_duration(counts["call_duration"]),
            "call_duration_seconds": counts["call_duration"],
        })

    if output_format == "json":
        return json.dumps(rows, indent=2, ensure_ascii=False)
    elif output_format == "csv":
        return _timeline_to_csv(rows)
    else:
        return _timeline_to_text(rows)


def _timeline_to_text(rows):
    """Render timeline as a fixed-width table."""
    lines = []
    lines.append("=== Timeline Report ===")
    lines.append("")

    header = f"{'Date':<12} {'SMS':>8} {'MMS':>8} {'Calls':>8} {'Call Duration':>14}"
    lines.append(header)
    lines.append("-" * len(header))

    for r in rows:
        lines.append(
            f"{r['date']:<12} {r['sms']:>8,} {r['mms']:>8,} "
            f"{r['calls']:>8,} {r['call_duration']:>14}"
        )

    return "\n".join(lines)


def _timeline_to_csv(rows):
    """Render timeline as CSV."""
    buf = io.StringIO()
    fieldnames = ["date", "sms", "mms", "calls", "call_duration", "call_duration_seconds"]
    writer = csv.DictWriter(buf, fieldnames=fieldnames)
    writer.writeheader()
    for r in rows:
        writer.writerow(r)
    return buf.getvalue()


# ---------------------------------------------------------------------------
# 4. Dispatcher
# ---------------------------------------------------------------------------

_REPORT_GENERATORS = {
    "summary": lambda data, fmt, **kw: generate_summary(data, output_format=fmt),
    "contacts": lambda data, fmt, **kw: generate_contacts(
        data, output_format=fmt, top_n=kw.get("top_n", 20)
    ),
    "timeline": lambda data, fmt, **kw: generate_timeline(data, output_format=fmt),
}


def generate_report(data, report_type="summary", output_format="text", top_n=20):
    """Generate one or all report types.

    If report_type is 'all', concatenate all reports with separators.
    """
    if report_type == "all":
        parts = []
        for name in ("summary", "contacts", "timeline"):
            parts.append(
                _REPORT_GENERATORS[name](data, output_format, top_n=top_n)
            )
        separator = "\n\n" if output_format == "text" else "\n"
        return separator.join(parts)

    generator = _REPORT_GENERATORS.get(report_type)
    if generator is None:
        raise ValueError(
            f"Unknown report type: {report_type!r}. "
            f"Valid types: {', '.join(sorted(_REPORT_GENERATORS))} or 'all'."
        )
    return generator(data, output_format, top_n=top_n)
