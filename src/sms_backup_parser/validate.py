"""JSON Schema validation for parser output."""

import json
import sys
from pathlib import Path


def _find_schema():
    """Locate the JSON schema, checking PyInstaller bundle first."""
    # PyInstaller --add-data puts files in sys._MEIPASS at runtime
    if hasattr(sys, '_MEIPASS'):
        bundled = Path(sys._MEIPASS) / "sms-backup-restore.schema.json"
        if bundled.exists():
            return bundled
    # Development: schema is at project root (3 levels up from this file)
    dev_path = Path(__file__).resolve().parent.parent.parent / "sms-backup-restore.schema.json"
    if dev_path.exists():
        return dev_path
    return None


SCHEMA_PATH = _find_schema()


def validate_output(json_path, schema_path=None):
    """Validate a parser output JSON file against the schema.

    Requires the 'jsonschema' package (pip install sms-backup-restore-parser[validate]).

    Raises:
        ImportError: If jsonschema is not installed.
        jsonschema.ValidationError: If validation fails.
    """
    try:
        import jsonschema
    except ImportError:
        raise ImportError(
            "jsonschema is required for validation. "
            "Install it with: pip install sms-backup-restore-parser[validate]"
        )

    schema_path = Path(schema_path) if schema_path else SCHEMA_PATH
    with open(schema_path, 'r', encoding='utf-8') as f:
        schema = json.load(f)
    with open(json_path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    jsonschema.validate(instance=data, schema=schema)
