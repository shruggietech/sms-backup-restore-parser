"""Tests for sms_backup_parser.parser writer classes."""

import json

from sms_backup_parser.parser import CombinedJsonWriter, JsonArrayWriter


def _load_json(path):
    with open(path, encoding='utf-8') as f:
        return json.load(f)


class TestJsonArrayWriter:
    """Unit tests for JsonArrayWriter."""

    def test_empty_array(self, tmp_path):
        path = tmp_path / "empty.json"
        with JsonArrayWriter(path):
            pass
        data = _load_json(path)
        assert data == []

    def test_single_record(self, tmp_path):
        path = tmp_path / "single.json"
        with JsonArrayWriter(path) as w:
            w.write_record({"key": "value"})
        data = _load_json(path)
        assert len(data) == 1
        assert data[0]["key"] == "value"

    def test_multiple_records(self, tmp_path):
        path = tmp_path / "multi.json"
        with JsonArrayWriter(path) as w:
            for i in range(5):
                w.write_record({"index": i})
        data = _load_json(path)
        assert len(data) == 5
        assert [r["index"] for r in data] == [0, 1, 2, 3, 4]

    def test_count_property(self, tmp_path):
        path = tmp_path / "count.json"
        with JsonArrayWriter(path) as w:
            w.write_record({"a": 1})
            w.write_record({"b": 2})
            assert w.count == 2

    def test_filepath_property(self, tmp_path):
        path = tmp_path / "fp.json"
        with JsonArrayWriter(path) as w:
            assert w.filepath == path

    def test_compact_output(self, tmp_path):
        path = tmp_path / "compact.json"
        with JsonArrayWriter(path, indent=None) as w:
            w.write_record({"key": "value"})
        content = path.read_text(encoding='utf-8')
        assert "    " not in content

    def test_unicode_content(self, tmp_path):
        path = tmp_path / "unicode.json"
        with JsonArrayWriter(path) as w:
            w.write_record({"body": "Hello \U0001f30d"})
        data = _load_json(path)
        assert "\U0001f30d" in data[0]["body"]


class TestCombinedJsonWriter:
    """Unit tests for CombinedJsonWriter."""

    def test_empty_combined(self, tmp_path):
        path = tmp_path / "empty_combined.json"
        with CombinedJsonWriter(path):
            pass
        data = _load_json(path)
        assert data == {"sms": [], "mms": [], "calls": []}

    def test_single_section(self, tmp_path):
        path = tmp_path / "sms_only.json"
        with CombinedJsonWriter(path) as w:
            w.write_record("sms", {"body": "test"})
            w.write_record("sms", {"body": "test2"})
        data = _load_json(path)
        assert len(data["sms"]) == 2
        assert data["mms"] == []
        assert data["calls"] == []

    def test_all_sections(self, tmp_path):
        path = tmp_path / "all.json"
        with CombinedJsonWriter(path) as w:
            w.write_record("sms", {"body": "sms1"})
            w.write_record("mms", {"sub": "mms1"})
            w.write_record("calls", {"number": "123"})
        data = _load_json(path)
        assert len(data["sms"]) == 1
        assert len(data["mms"]) == 1
        assert len(data["calls"]) == 1

    def test_interleaved_writes(self, tmp_path):
        path = tmp_path / "interleaved.json"
        with CombinedJsonWriter(path) as w:
            w.write_record("sms", {"body": "s1"})
            w.write_record("calls", {"number": "123"})
            w.write_record("sms", {"body": "s2"})
            w.write_record("mms", {"sub": "m1"})
        data = _load_json(path)
        assert len(data["sms"]) == 2
        assert len(data["mms"]) == 1
        assert len(data["calls"]) == 1

    def test_counts_property(self, tmp_path):
        path = tmp_path / "counts.json"
        with CombinedJsonWriter(path) as w:
            w.write_record("sms", {"body": "s1"})
            w.write_record("sms", {"body": "s2"})
            w.write_record("calls", {"number": "123"})
            counts = w.counts
        assert counts == {"sms": 2, "mms": 0, "calls": 1}

    def test_compact_output(self, tmp_path):
        path = tmp_path / "compact.json"
        with CombinedJsonWriter(path, indent=None) as w:
            w.write_record("sms", {"body": "test"})
        content = path.read_text(encoding='utf-8')
        assert "    " not in content
        data = _load_json(path)
        assert len(data["sms"]) == 1
