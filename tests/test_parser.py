"""Tests for sms_backup_parser.parser."""

import json
import xml.etree.ElementTree as ET

import pytest

from sms_backup_parser.parser import parse_backup


def _load_json(path):
    with open(path, encoding='utf-8') as f:
        return json.load(f)


class TestParseMinimalSms:
    """Parse minimal_sms.xml and verify SMS extraction."""

    def test_counts(self, minimal_sms_xml, tmp_path):
        result = parse_backup(minimal_sms_xml, output_dir=tmp_path, combined=True)
        assert result["sms_count"] == 1
        assert result["mms_count"] == 0
        assert result["call_count"] == 0

    def test_sms_fields(self, minimal_sms_xml, tmp_path):
        result = parse_backup(minimal_sms_xml, output_dir=tmp_path, combined=True)
        data = _load_json(result["output_files"][0])
        sms = data["sms"][0]
        assert sms["address"] == "+15551234567"
        assert sms["date_iso"] == "2021-01-01T00:00:00+00:00"
        assert sms["body"] == "Happy New Year! This is a test message."


class TestParseMinimalMms:
    """Parse minimal_mms.xml and verify MMS extraction."""

    def test_mms_count(self, minimal_mms_xml, tmp_path):
        result = parse_backup(minimal_mms_xml, output_dir=tmp_path, combined=True)
        assert result["mms_count"] == 1

    def test_mms_parts(self, minimal_mms_xml, tmp_path):
        result = parse_backup(minimal_mms_xml, output_dir=tmp_path, combined=True)
        data = _load_json(result["output_files"][0])
        mms = data["mms"][0]
        assert len(mms["parts"]) == 3
        assert mms["parts"][1]["text"] == "Hello from MMS!"

    def test_mms_addrs(self, minimal_mms_xml, tmp_path):
        result = parse_backup(minimal_mms_xml, output_dir=tmp_path, combined=True)
        data = _load_json(result["output_files"][0])
        mms = data["mms"][0]
        assert len(mms["addrs"]) == 2
        assert mms["addrs"][0]["type"] == "137"


class TestParseMinimalCalls:
    """Parse minimal_calls.xml and verify call log extraction."""

    def test_call_count(self, minimal_calls_xml, tmp_path):
        result = parse_backup(minimal_calls_xml, output_dir=tmp_path, combined=True)
        assert result["call_count"] == 1

    def test_call_fields(self, minimal_calls_xml, tmp_path):
        result = parse_backup(minimal_calls_xml, output_dir=tmp_path, combined=True)
        data = _load_json(result["output_files"][0])
        call = data["calls"][0]
        assert call["number"] == "+15551234567"
        assert call["duration"] == "125"


class TestParseMixed:
    """Parse mixed.xml containing SMS, MMS, and verify counts."""

    def test_mixed_counts(self, mixed_xml, tmp_path):
        result = parse_backup(mixed_xml, output_dir=tmp_path, combined=True)
        assert result["sms_count"] == 3
        assert result["mms_count"] == 1
        assert result["call_count"] == 0


class TestParseSeparateFiles:
    """Parse in default separate-file mode."""

    def test_creates_sms_file_only(self, minimal_sms_xml, tmp_path):
        result = parse_backup(minimal_sms_xml, output_dir=tmp_path)
        output_files = result["output_files"]
        # Should have exactly one output file for SMS
        assert len(output_files) == 1
        assert output_files[0].endswith("_sms.json")

    def test_no_mms_or_calls_files(self, minimal_sms_xml, tmp_path):
        parse_backup(minimal_sms_xml, output_dir=tmp_path)
        files = list(tmp_path.iterdir())
        names = [f.name for f in files]
        assert not any("_mms.json" in n for n in names)
        assert not any("_calls.json" in n for n in names)


class TestParseStripMedia:
    """Verify strip_media removes base64 data from MMS parts."""

    def test_no_data_key(self, minimal_mms_xml, tmp_path):
        result = parse_backup(
            minimal_mms_xml, output_dir=tmp_path, combined=True, strip_media=True
        )
        data = _load_json(result["output_files"][0])
        for part in data["mms"][0]["parts"]:
            assert "data" not in part


class TestParseNoDateIso:
    """Verify inject_date_iso=False omits the computed field."""

    def test_date_iso_absent(self, minimal_sms_xml, tmp_path):
        result = parse_backup(
            minimal_sms_xml, output_dir=tmp_path, combined=True, inject_date_iso=False
        )
        data = _load_json(result["output_files"][0])
        sms = data["sms"][0]
        assert "date_iso" not in sms


class TestParseMalformed:
    """Malformed XML raises a parse error."""

    def test_raises_parse_error(self, malformed_xml, tmp_path):
        with pytest.raises(ET.ParseError):
            parse_backup(malformed_xml, output_dir=tmp_path, combined=True)


class TestParseEdgeCases:
    """Edge case XML parses without crashing."""

    def test_does_not_crash(self, edge_cases_xml, tmp_path):
        result = parse_backup(edge_cases_xml, output_dir=tmp_path, combined=True)
        assert result["sms_count"] >= 1

    def test_unicode_body(self, edge_cases_xml, tmp_path):
        result = parse_backup(edge_cases_xml, output_dir=tmp_path, combined=True)
        data = _load_json(result["output_files"][0])
        # The second SMS has unicode chars including globe emoji U+1F30D
        bodies = [sms["body"] for sms in data["sms"]]
        assert any("\U0001f30d" in body for body in bodies)


class TestParseOutputDir:
    """Output is written to the specified directory."""

    def test_output_in_subdir(self, minimal_sms_xml, tmp_path):
        subdir = tmp_path / "subdir"
        subdir.mkdir()
        result = parse_backup(minimal_sms_xml, output_dir=subdir, combined=True)
        assert len(result["output_files"]) == 1
        from pathlib import Path
        assert Path(result["output_files"][0]).parent == subdir


class TestParseMultiFileCombined:
    """Multi-file combined mode merges all records into one output."""

    def test_single_output_file(self, minimal_sms_xml, minimal_calls_xml, tmp_path):
        from sms_backup_parser.parser import parse_backup_multi
        result = parse_backup_multi(
            [minimal_sms_xml, minimal_calls_xml], output_dir=tmp_path
        )
        assert len(result["output_files"]) == 1

    def test_merged_counts(self, minimal_sms_xml, minimal_calls_xml, tmp_path):
        from sms_backup_parser.parser import parse_backup_multi
        result = parse_backup_multi(
            [minimal_sms_xml, minimal_calls_xml], output_dir=tmp_path
        )
        assert result["sms_count"] == 1
        assert result["call_count"] == 1

    def test_merged_json_structure(self, minimal_sms_xml, minimal_calls_xml, tmp_path):
        from sms_backup_parser.parser import parse_backup_multi
        result = parse_backup_multi(
            [minimal_sms_xml, minimal_calls_xml], output_dir=tmp_path
        )
        data = _load_json(result["output_files"][0])
        assert len(data["sms"]) == 1
        assert len(data["calls"]) == 1
        assert len(data["mms"]) == 0

    def test_all_three_types_merged(self, minimal_sms_xml, minimal_mms_xml,
                                     minimal_calls_xml, tmp_path):
        from sms_backup_parser.parser import parse_backup_multi
        result = parse_backup_multi(
            [minimal_sms_xml, minimal_mms_xml, minimal_calls_xml],
            output_dir=tmp_path,
        )
        data = _load_json(result["output_files"][0])
        assert len(data["sms"]) == 1
        assert len(data["mms"]) == 1
        assert len(data["calls"]) == 1

    def test_output_uses_first_file_stem(self, minimal_sms_xml, minimal_calls_xml, tmp_path):
        from sms_backup_parser.parser import parse_backup_multi
        result = parse_backup_multi(
            [minimal_sms_xml, minimal_calls_xml], output_dir=tmp_path
        )
        from pathlib import Path
        assert Path(result["output_files"][0]).stem == minimal_sms_xml.stem

    def test_file_not_found_raises(self, minimal_sms_xml, tmp_path):
        from sms_backup_parser.parser import parse_backup_multi
        with pytest.raises(FileNotFoundError):
            parse_backup_multi(
                [minimal_sms_xml, tmp_path / "nonexistent.xml"],
                output_dir=tmp_path,
            )

    def test_compact_output(self, minimal_sms_xml, minimal_calls_xml, tmp_path):
        from sms_backup_parser.parser import parse_backup_multi
        result = parse_backup_multi(
            [minimal_sms_xml, minimal_calls_xml], output_dir=tmp_path, indent=None
        )
        content = open(result["output_files"][0], encoding='utf-8').read()
        assert "    " not in content


class TestParseCompactOutput:
    """Verify compact (indent=None) output produces minimal whitespace."""

    def test_compact_combined(self, minimal_sms_xml, tmp_path):
        result = parse_backup(
            minimal_sms_xml, output_dir=tmp_path, combined=True, indent=None
        )
        content = open(result["output_files"][0], encoding='utf-8').read()
        assert "    " not in content

    def test_compact_separate(self, minimal_sms_xml, tmp_path):
        result = parse_backup(
            minimal_sms_xml, output_dir=tmp_path, indent=None
        )
        content = open(result["output_files"][0], encoding='utf-8').read()
        assert "    " not in content
