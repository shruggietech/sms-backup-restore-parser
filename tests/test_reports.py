"""Tests for the sms_backup_parser.reports module."""

import csv
import io
import json

import pytest

from sms_backup_parser.reports import (
    generate_contacts,
    generate_report,
    generate_timeline,
)

# ---------------------------------------------------------------------------
# Fixture data — minimal synthetic records for report generation
# ---------------------------------------------------------------------------

@pytest.fixture
def sample_data():
    """Return a minimal data dict with sms, mms, and calls lists."""
    return {
        "sms": [
            {
                "address": "+15551234567",
                "contact_name": "Alice Smith",
                "type": "1",
                "date_iso": "2024-01-01T10:00:00+00:00",
                "body": "Hello",
            },
            {
                "address": "+15551234567",
                "contact_name": "Alice Smith",
                "type": "2",
                "date_iso": "2024-01-01T11:00:00+00:00",
                "body": "Hi back",
            },
            {
                "address": "+15559990001",
                "contact_name": "Bob Jones",
                "type": "1",
                "date_iso": "2024-01-02T09:00:00+00:00",
                "body": "Hey",
            },
        ],
        "mms": [
            {
                "address": "+15551234567",
                "contact_name": "Alice Smith",
                "msg_box": "1",
                "text_only": "1",
                "date_iso": "2024-01-01T12:00:00+00:00",
            },
        ],
        "calls": [
            {
                "number": "+15551234567",
                "contact_name": "Alice Smith",
                "type": "1",
                "duration": "60",
                "date_iso": "2024-01-01T08:00:00+00:00",
            },
            {
                "number": "+15551234567",
                "contact_name": "Alice Smith",
                "type": "2",
                "duration": "120",
                "date_iso": "2024-01-02T14:00:00+00:00",
            },
        ],
    }


# ---------------------------------------------------------------------------
# generate_report() return type
# ---------------------------------------------------------------------------

class TestGenerateReportReturnType:
    """generate_report() always returns dict[str, str]."""

    def test_single_type_returns_one_entry(self, sample_data):
        result = generate_report(sample_data, report_type="summary")
        assert isinstance(result, dict)
        assert list(result.keys()) == ["summary"]

    def test_all_returns_three_entries(self, sample_data):
        result = generate_report(sample_data, report_type="all")
        assert isinstance(result, dict)
        assert set(result.keys()) == {"summary", "contacts", "timeline"}

    def test_each_type_returns_dict(self, sample_data):
        for rtype in ("summary", "contacts", "timeline"):
            result = generate_report(sample_data, report_type=rtype)
            assert isinstance(result, dict)
            assert rtype in result

    def test_unknown_type_raises(self, sample_data):
        with pytest.raises(ValueError, match="Unknown report type"):
            generate_report(sample_data, report_type="nonexistent")


# ---------------------------------------------------------------------------
# CSV output quality
# ---------------------------------------------------------------------------

class TestCsvOutput:
    """CSV output is well-formed with no double newlines."""

    def test_summary_csv_no_double_newlines(self, sample_data):
        result = generate_report(sample_data, report_type="summary", output_format="csv")
        content = result["summary"]
        assert "\r\r" not in content
        # Should parse as valid CSV
        reader = csv.reader(io.StringIO(content))
        rows = list(reader)
        assert rows[0] == ["key", "value"]
        assert len(rows) > 1

    def test_contacts_csv_no_double_newlines(self, sample_data):
        result = generate_report(sample_data, report_type="contacts", output_format="csv")
        content = result["contacts"]
        assert "\r\r" not in content
        reader = csv.DictReader(io.StringIO(content))
        rows = list(reader)
        assert len(rows) >= 1
        assert "contact" in reader.fieldnames

    def test_timeline_csv_no_double_newlines(self, sample_data):
        result = generate_report(sample_data, report_type="timeline", output_format="csv")
        content = result["timeline"]
        assert "\r\r" not in content
        reader = csv.DictReader(io.StringIO(content))
        rows = list(reader)
        assert len(rows) >= 1
        assert "date" in reader.fieldnames

    def test_all_csv_produces_separate_valid_csvs(self, sample_data):
        result = generate_report(sample_data, report_type="all", output_format="csv")
        for name, content in result.items():
            assert "\r\r" not in content
            reader = csv.reader(io.StringIO(content))
            rows = list(reader)
            assert len(rows) >= 2, f"{name} CSV has fewer than 2 rows"


# ---------------------------------------------------------------------------
# JSON output quality
# ---------------------------------------------------------------------------

class TestJsonOutput:
    """JSON output is valid and parseable."""

    def test_summary_json_valid(self, sample_data):
        result = generate_report(sample_data, report_type="summary", output_format="json")
        parsed = json.loads(result["summary"])
        assert "sms_count" in parsed

    def test_contacts_json_valid(self, sample_data):
        result = generate_report(sample_data, report_type="contacts", output_format="json")
        parsed = json.loads(result["contacts"])
        assert isinstance(parsed, list)

    def test_timeline_json_valid(self, sample_data):
        result = generate_report(sample_data, report_type="timeline", output_format="json")
        parsed = json.loads(result["timeline"])
        assert isinstance(parsed, list)


# ---------------------------------------------------------------------------
# Text output quality
# ---------------------------------------------------------------------------

class TestTextOutput:
    """Text output contains expected section headers."""

    def test_summary_text_has_header(self, sample_data):
        result = generate_report(sample_data, report_type="summary", output_format="text")
        assert "Backup Summary" in result["summary"]

    def test_contacts_text_has_header(self, sample_data):
        result = generate_report(sample_data, report_type="contacts", output_format="text")
        assert "Contacts Report" in result["contacts"]

    def test_timeline_text_has_header(self, sample_data):
        result = generate_report(sample_data, report_type="timeline", output_format="text")
        assert "Timeline Report" in result["timeline"]


# ---------------------------------------------------------------------------
# top_n behavior
# ---------------------------------------------------------------------------

class TestTopN:
    """top_n=0 means all contacts; positive values limit output."""

    def test_top_n_zero_returns_all(self, sample_data):
        result = generate_contacts(sample_data, output_format="json", top_n=0)
        contacts = json.loads(result)
        # sample_data has 2 unique contacts (Alice + Bob)
        assert len(contacts) == 2

    def test_top_n_one_returns_one(self, sample_data):
        result = generate_contacts(sample_data, output_format="json", top_n=1)
        contacts = json.loads(result)
        assert len(contacts) == 1

    def test_top_n_larger_than_total(self, sample_data):
        result = generate_contacts(sample_data, output_format="json", top_n=100)
        contacts = json.loads(result)
        assert len(contacts) == 2


# ---------------------------------------------------------------------------
# Empty data
# ---------------------------------------------------------------------------

class TestEmptyData:
    """Reports handle empty datasets gracefully."""

    def test_summary_empty(self):
        data = {"sms": [], "mms": [], "calls": []}
        result = generate_report(data, report_type="summary")
        assert "summary" in result

    def test_contacts_empty_csv(self):
        data = {"sms": [], "mms": [], "calls": []}
        result = generate_contacts(data, output_format="csv")
        assert "No contact data" in result

    def test_timeline_empty_json(self):
        data = {"sms": [], "mms": [], "calls": []}
        result = generate_timeline(data, output_format="json")
        assert json.loads(result) == []
