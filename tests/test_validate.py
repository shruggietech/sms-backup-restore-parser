"""Tests for sms_backup_parser.validate."""

import json

import pytest

from sms_backup_parser.validate import SCHEMA_PATH, validate_output


class TestSchemaDiscovery:
    """Verify the schema file can be located."""

    def test_schema_path_exists(self):
        assert SCHEMA_PATH is not None
        assert SCHEMA_PATH.exists()

    def test_schema_is_valid_json(self):
        assert SCHEMA_PATH is not None
        with open(SCHEMA_PATH, 'r', encoding='utf-8') as f:
            schema = json.load(f)
        assert "$schema" in schema or "type" in schema


class TestValidateOutput:
    """Validate output files against the JSON schema."""

    def test_valid_combined_output(self, minimal_sms_xml, tmp_path):
        from sms_backup_parser.parser import parse_backup
        result = parse_backup(minimal_sms_xml, output_dir=tmp_path, combined=True)
        try:
            validate_output(result["output_files"][0])
        except ImportError:
            pytest.skip("jsonschema not installed")

    def test_invalid_data_raises(self, tmp_path):
        bad_file = tmp_path / "bad.json"
        bad_file.write_text('{"invalid": "data"}', encoding='utf-8')
        try:
            import jsonschema
            with pytest.raises(jsonschema.ValidationError):
                validate_output(str(bad_file))
        except ImportError:
            pytest.skip("jsonschema not installed")
