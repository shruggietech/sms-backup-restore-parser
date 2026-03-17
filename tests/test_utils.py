"""Tests for sms_backup_parser.utils."""

from sms_backup_parser.utils import java_epoch_to_iso, format_file_size


class TestJavaEpochToIso:
    """Test java_epoch_to_iso conversion."""

    def test_valid_timestamp(self):
        result = java_epoch_to_iso("1609459200000")
        assert result == "2021-01-01T00:00:00+00:00"

    def test_zero_returns_none(self):
        assert java_epoch_to_iso("0") is None

    def test_empty_string_returns_none(self):
        assert java_epoch_to_iso("") is None

    def test_none_returns_none(self):
        assert java_epoch_to_iso(None) is None

    def test_non_numeric_returns_none(self):
        assert java_epoch_to_iso("abc") is None

    def test_negative_returns_none(self):
        # str.isdigit() returns False for "-1"
        assert java_epoch_to_iso("-1") is None

    def test_very_large_valid_timestamp(self):
        # 2100-01-01T00:00:00Z = 4102444800000 ms
        result = java_epoch_to_iso("4102444800000")
        assert result is not None
        assert result == "2100-01-01T00:00:00+00:00"


class TestFormatFileSize:
    """Test format_file_size human-readable output."""

    def test_zero_bytes(self):
        assert format_file_size(0) == "0.0 B"

    def test_one_kilobyte(self):
        assert format_file_size(1024) == "1.0 KB"

    def test_one_megabyte(self):
        assert format_file_size(1048576) == "1.0 MB"

    def test_one_gigabyte(self):
        assert format_file_size(1073741824) == "1.0 GB"
