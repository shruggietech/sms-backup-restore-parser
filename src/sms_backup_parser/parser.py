"""Streaming XML-to-JSON parser for SMS Backup & Restore exports.

Handles SMS, MMS, and call log XML files produced by SyncTech's SMS Backup &
Restore app. Uses iterparse for constant-memory processing of multi-gigabyte
backup files. Writes JSON output incrementally via JsonArrayWriter /
CombinedJsonWriter to avoid accumulating records in memory.
"""

import json
import xml.etree.ElementTree as ET
from pathlib import Path

from .utils import java_epoch_to_iso


class JsonArrayWriter:
    """Write a JSON array incrementally to a file.

    Usage as a context manager:
        with JsonArrayWriter(path) as w:
            w.write_record({"key": "value"})
    """

    def __init__(self, filepath, indent=2):
        self._filepath = Path(filepath)
        self._indent = indent
        self._file = None
        self._count = 0

    def __enter__(self):
        self._file = open(self._filepath, 'w', encoding='utf-8')
        self._file.write('[\n')
        return self

    def write_record(self, record):
        """Append one record to the JSON array."""
        if self._count > 0:
            self._file.write(',\n')
        json.dump(record, self._file, indent=self._indent, ensure_ascii=False)
        self._count += 1

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self._file:
            if self._count > 0:
                self._file.write('\n')
            self._file.write(']\n')
            self._file.close()
        return False

    @property
    def count(self):
        return self._count

    @property
    def filepath(self):
        return self._filepath


class CombinedJsonWriter:
    """Write a combined JSON object with sms/mms/calls arrays incrementally.

    Produces: {"sms": [...], "mms": [...], "calls": [...]}
    Records may arrive in any order (interleaved SMS/MMS/calls). Each section
    is written to a temporary file, then assembled on close.
    """

    SECTIONS = ("sms", "mms", "calls")

    def __init__(self, filepath, indent=2):
        self._filepath = Path(filepath)
        self._indent = indent
        self._counts = {s: 0 for s in self.SECTIONS}
        self._section_writers = {}

    def __enter__(self):
        import tempfile
        self._tmpdir = tempfile.mkdtemp()
        for section in self.SECTIONS:
            tmp_path = Path(self._tmpdir) / f"{section}.json"
            writer = JsonArrayWriter(tmp_path, indent=self._indent)
            writer.__enter__()
            self._section_writers[section] = writer
        return self

    def write_record(self, section, record):
        """Append a record to the named section."""
        self._section_writers[section].write_record(record)
        self._counts[section] += 1

    def __exit__(self, exc_type, exc_val, exc_tb):
        import shutil
        # Close all temporary writers
        for writer in self._section_writers.values():
            writer.__exit__(None, None, None)

        # Assemble the combined file from temp arrays
        try:
            with open(self._filepath, 'w', encoding='utf-8') as out:
                out.write('{\n')
                for i, section in enumerate(self.SECTIONS):
                    tmp_path = self._section_writers[section].filepath
                    out.write(f'  "{section}": ')
                    with open(tmp_path, 'r', encoding='utf-8') as tmp:
                        content = tmp.read().rstrip('\n')
                    out.write(content)
                    if i < len(self.SECTIONS) - 1:
                        out.write(',')
                    out.write('\n')
                out.write('}\n')
        finally:
            shutil.rmtree(self._tmpdir, ignore_errors=True)

        return False

    @property
    def counts(self):
        return dict(self._counts)

    @property
    def filepath(self):
        return self._filepath


def _extract_sms(elem, inject_date_iso):
    """Extract an SMS record from an element."""
    record = dict(elem.attrib)
    if inject_date_iso:
        iso = java_epoch_to_iso(record.get("date"))
        if iso:
            record["date_iso"] = iso
    return record


def _extract_mms(elem, inject_date_iso, strip_media):
    """Extract an MMS record with nested parts and addrs."""
    record = dict(elem.attrib)
    if inject_date_iso:
        iso = java_epoch_to_iso(record.get("date"))
        if iso:
            record["date_iso"] = iso

    # Collect parts
    parts = []
    for part_elem in elem.findall('.//part'):
        part = dict(part_elem.attrib)
        if strip_media:
            part.pop('data', None)
        parts.append(part)
    if parts:
        record['parts'] = parts

    # Collect addresses
    addrs = []
    for addr_elem in elem.findall('.//addr'):
        addrs.append(dict(addr_elem.attrib))
    if addrs:
        record['addrs'] = addrs

    return record


def _extract_call(elem, inject_date_iso):
    """Extract a call log record from an element."""
    record = dict(elem.attrib)
    if inject_date_iso:
        iso = java_epoch_to_iso(record.get("date"))
        if iso:
            record["date_iso"] = iso
    return record


def parse_backup(input_path, output_dir=None, combined=False, strip_media=False,
                 inject_date_iso=True, indent=2, progress_tracker=None):
    """Parse an SMS Backup & Restore XML file into JSON.

    Args:
        input_path: Path to the XML backup file.
        output_dir: Directory for output files. Defaults to same directory as input.
        combined: If True, write single combined JSON file instead of per-type files.
        strip_media: If True, omit base64 'data' attribute from MMS parts.
        inject_date_iso: If True, add computed date_iso fields.
        indent: JSON indentation level (None for compact).
        progress_tracker: Optional ProgressTracker instance.

    Returns:
        dict with keys 'sms_count', 'mms_count', 'call_count', 'output_files'.

    Raises:
        FileNotFoundError: If input_path does not exist.
        PermissionError: If input_path is not readable.
        xml.etree.ElementTree.ParseError: If XML is malformed.
    """
    input_path = Path(input_path)

    # Input validation
    if not input_path.exists():
        raise FileNotFoundError(f"Input file not found: {input_path}")
    if not input_path.is_file():
        raise FileNotFoundError(f"Not a file: {input_path}")
    if input_path.stat().st_size == 0:
        raise ValueError(f"Input file is empty: {input_path}")

    # Determine output directory
    if output_dir is None:
        output_dir = input_path.parent
    else:
        output_dir = Path(output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)

    stem = input_path.stem

    if progress_tracker:
        progress_tracker.start()

    if combined:
        return _parse_combined(
            input_path, output_dir, stem, strip_media,
            inject_date_iso, indent, progress_tracker
        )
    else:
        return _parse_separate(
            input_path, output_dir, stem, strip_media,
            inject_date_iso, indent, progress_tracker
        )


def _parse_separate(input_path, output_dir, stem, strip_media,
                    inject_date_iso, indent, progress_tracker):
    """Parse into separate per-type JSON files."""
    writers = {}
    output_files = []
    counts = {"sms": 0, "mms": 0, "call": 0}

    # Map record types to output filenames
    file_map = {
        "sms": output_dir / f"{stem}_sms.json",
        "mms": output_dir / f"{stem}_mms.json",
        "call": output_dir / f"{stem}_calls.json",
    }

    try:
        context = ET.iterparse(str(input_path), events=('end',))

        for event, elem in context:
            tag = elem.tag

            if tag == 'sms':
                record = _extract_sms(elem, inject_date_iso)
                if "sms" not in writers:
                    writers["sms"] = JsonArrayWriter(file_map["sms"], indent=indent)
                    writers["sms"].__enter__()
                writers["sms"].write_record(record)
                counts["sms"] += 1
                if progress_tracker:
                    if progress_tracker._verbosity >= 2:
                        progress_tracker.update_verbose("sms", record)
                    else:
                        progress_tracker.update("sms")
                elem.clear()

            elif tag == 'mms':
                record = _extract_mms(elem, inject_date_iso, strip_media)
                if "mms" not in writers:
                    writers["mms"] = JsonArrayWriter(file_map["mms"], indent=indent)
                    writers["mms"].__enter__()
                writers["mms"].write_record(record)
                counts["mms"] += 1
                if progress_tracker:
                    if progress_tracker._verbosity >= 2:
                        progress_tracker.update_verbose("mms", record)
                    else:
                        progress_tracker.update("mms")
                elem.clear()

            elif tag == 'call':
                record = _extract_call(elem, inject_date_iso)
                if "call" not in writers:
                    writers["call"] = JsonArrayWriter(file_map["call"], indent=indent)
                    writers["call"].__enter__()
                writers["call"].write_record(record)
                counts["call"] += 1
                if progress_tracker:
                    if progress_tracker._verbosity >= 2:
                        progress_tracker.update_verbose("call", record)
                    else:
                        progress_tracker.update("call")
                elem.clear()

    except ET.ParseError as e:
        raise ET.ParseError(
            f"Malformed XML in {input_path}: {e}"
        ) from e
    finally:
        # Close all opened writers
        for writer in writers.values():
            writer.__exit__(None, None, None)

    # Collect output file paths for writers that actually wrote records
    for rtype, writer in writers.items():
        if writer.count > 0:
            output_files.append(str(writer.filepath))

    if progress_tracker:
        progress_tracker.finish()

    return {
        "sms_count": counts["sms"],
        "mms_count": counts["mms"],
        "call_count": counts["call"],
        "output_files": output_files,
    }


def _parse_combined(input_path, output_dir, stem, strip_media,
                    inject_date_iso, indent, progress_tracker):
    """Parse into a single combined JSON file."""
    output_path = output_dir / f"{stem}.json"
    counts = {"sms": 0, "mms": 0, "call": 0}

    # Map XML tags to combined section names
    tag_to_section = {
        "sms": "sms",
        "mms": "mms",
        "call": "calls",
    }

    try:
        with CombinedJsonWriter(output_path, indent=indent) as writer:
            context = ET.iterparse(str(input_path), events=('end',))

            for event, elem in context:
                tag = elem.tag

                if tag == 'sms':
                    record = _extract_sms(elem, inject_date_iso)
                    writer.write_record("sms", record)
                    counts["sms"] += 1
                    if progress_tracker:
                        if progress_tracker._verbosity >= 2:
                            progress_tracker.update_verbose("sms", record)
                        else:
                            progress_tracker.update("sms")
                    elem.clear()

                elif tag == 'mms':
                    record = _extract_mms(elem, inject_date_iso, strip_media)
                    writer.write_record("mms", record)
                    counts["mms"] += 1
                    if progress_tracker:
                        if progress_tracker._verbosity >= 2:
                            progress_tracker.update_verbose("mms", record)
                        else:
                            progress_tracker.update("mms")
                    elem.clear()

                elif tag == 'call':
                    record = _extract_call(elem, inject_date_iso)
                    writer.write_record("calls", record)
                    counts["call"] += 1
                    if progress_tracker:
                        if progress_tracker._verbosity >= 2:
                            progress_tracker.update_verbose("call", record)
                        else:
                            progress_tracker.update("call")
                    elem.clear()

    except ET.ParseError as e:
        raise ET.ParseError(
            f"Malformed XML in {input_path}: {e}"
        ) from e

    if progress_tracker:
        progress_tracker.finish()

    output_files = [str(output_path)] if any(counts.values()) else []

    return {
        "sms_count": counts["sms"],
        "mms_count": counts["mms"],
        "call_count": counts["call"],
        "output_files": output_files,
    }


def parse_backup_multi(input_paths, output_dir, strip_media=False,
                       inject_date_iso=True, indent=2, progress_tracker_factory=None):
    """Parse multiple XML files into a single combined JSON output.

    Merges all SMS, MMS, and call records from all input files into one
    combined JSON file with top-level 'sms', 'mms', and 'calls' arrays.

    Args:
        input_paths: List of Path objects to XML backup files.
        output_dir: Directory for the output file.
        strip_media: If True, omit base64 'data' attribute from MMS parts.
        inject_date_iso: If True, add computed date_iso fields.
        indent: JSON indentation level (None for compact).
        progress_tracker_factory: Optional callable returning a ProgressTracker.

    Returns:
        dict with keys 'sms_count', 'mms_count', 'call_count', 'output_files'.
    """
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    stem = Path(input_paths[0]).stem
    output_path = output_dir / f"{stem}.json"
    total_counts = {"sms": 0, "mms": 0, "call": 0}

    with CombinedJsonWriter(output_path, indent=indent) as writer:
        for input_path in input_paths:
            input_path = Path(input_path)

            if not input_path.exists():
                raise FileNotFoundError(f"Input file not found: {input_path}")
            if not input_path.is_file():
                raise FileNotFoundError(f"Not a file: {input_path}")

            progress_tracker = None
            if progress_tracker_factory:
                progress_tracker = progress_tracker_factory()
                progress_tracker.start()

            try:
                context = ET.iterparse(str(input_path), events=('end',))

                for event, elem in context:
                    tag = elem.tag

                    if tag == 'sms':
                        record = _extract_sms(elem, inject_date_iso)
                        writer.write_record("sms", record)
                        total_counts["sms"] += 1
                        if progress_tracker:
                            if progress_tracker._verbosity >= 2:
                                progress_tracker.update_verbose("sms", record)
                            else:
                                progress_tracker.update("sms")
                        elem.clear()

                    elif tag == 'mms':
                        record = _extract_mms(elem, inject_date_iso, strip_media)
                        writer.write_record("mms", record)
                        total_counts["mms"] += 1
                        if progress_tracker:
                            if progress_tracker._verbosity >= 2:
                                progress_tracker.update_verbose("mms", record)
                            else:
                                progress_tracker.update("mms")
                        elem.clear()

                    elif tag == 'call':
                        record = _extract_call(elem, inject_date_iso)
                        writer.write_record("calls", record)
                        total_counts["call"] += 1
                        if progress_tracker:
                            if progress_tracker._verbosity >= 2:
                                progress_tracker.update_verbose("call", record)
                            else:
                                progress_tracker.update("call")
                        elem.clear()

            except ET.ParseError as e:
                raise ET.ParseError(
                    f"Malformed XML in {input_path}: {e}"
                ) from e

            if progress_tracker:
                progress_tracker.finish()

    output_files = [str(output_path)] if any(total_counts.values()) else []

    return {
        "sms_count": total_counts["sms"],
        "mms_count": total_counts["mms"],
        "call_count": total_counts["call"],
        "output_files": output_files,
    }
