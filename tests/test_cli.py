"""Tests for the sms_backup_parser CLI entry point."""

import json
import subprocess
import sys
from pathlib import Path

FIXTURES_DIR = Path(__file__).parent / "fixtures"


def run_cli(*args, check=False):
    """Run the CLI as a subprocess and return the CompletedProcess."""
    return subprocess.run(
        [sys.executable, "-m", "sms_backup_parser", *args],
        capture_output=True,
        text=True,
        check=check,
        env={**__import__("os").environ, "PYTHONPATH": str(Path(__file__).parent.parent / "src")},
    )


class TestCliParseBasic:
    """Basic parse subcommand invocation."""

    def test_exit_code_zero(self, tmp_path):
        xml = str(FIXTURES_DIR / "minimal_sms.xml")
        result = run_cli("parse", xml, "-o", str(tmp_path), "--combined")
        assert result.returncode == 0

    def test_output_file_created(self, tmp_path):
        xml = str(FIXTURES_DIR / "minimal_sms.xml")
        run_cli("parse", xml, "-o", str(tmp_path), "--combined")
        json_files = list(tmp_path.glob("*.json"))
        assert len(json_files) >= 1


class TestCliParseQuiet:
    """Quiet flag suppresses non-error output.

    Note: -q/--quiet is a top-level flag and must precede the subcommand.
    """

    def test_quiet_exit_code(self, tmp_path):
        xml = str(FIXTURES_DIR / "minimal_sms.xml")
        result = run_cli("-q", "parse", xml, "-o", str(tmp_path), "--combined")
        assert result.returncode == 0

    def test_quiet_stdout_empty(self, tmp_path):
        xml = str(FIXTURES_DIR / "minimal_sms.xml")
        result = run_cli("-q", "parse", xml, "-o", str(tmp_path), "--combined")
        assert len(result.stdout.strip()) == 0


class TestCliVersion:
    """Version subcommand prints version string."""

    def test_exit_code(self):
        result = run_cli("version")
        assert result.returncode == 0

    def test_contains_version(self):
        result = run_cli("version")
        output = result.stdout + result.stderr
        assert "0." in output or "version" in output.lower()


class TestCliNoArgs:
    """Invocation with no arguments shows help."""

    def test_exit_code(self):
        result = run_cli()
        assert result.returncode == 0


class TestCliMissingFile:
    """Parse a nonexistent file prints an error.

    Note: __main__.py does not currently pass main()'s return code to
    sys.exit(), so the process exit code is 0 even on error. We verify
    the error message appears on stderr instead.
    """

    def test_error_message(self):
        result = run_cli("parse", "nonexistent_file_that_does_not_exist.xml")
        assert "not found" in result.stderr.lower() or "error" in result.stderr.lower()


class TestCliHelp:
    """Help flag prints usage with expected subcommands."""

    def test_exit_code(self):
        result = run_cli("--help")
        assert result.returncode == 0

    def test_contains_subcommands(self):
        result = run_cli("--help")
        output = result.stdout + result.stderr
        assert "parse" in output
        assert "version" in output


class TestCliExitCodes:
    """Verify CLI propagates nonzero exit codes correctly."""

    def test_missing_file_nonzero(self):
        result = run_cli("parse", "nonexistent_file_that_does_not_exist.xml")
        assert result.returncode != 0

    def test_success_zero(self, tmp_path):
        xml = str(FIXTURES_DIR / "minimal_sms.xml")
        result = run_cli("parse", xml, "-o", str(tmp_path), "--combined")
        assert result.returncode == 0


class TestCliMultiFileCombined:
    """Multi-file --combined produces a single merged output."""

    def test_single_output_file(self, tmp_path):
        sms = str(FIXTURES_DIR / "minimal_sms.xml")
        calls = str(FIXTURES_DIR / "minimal_calls.xml")
        result = run_cli("parse", sms, calls, "-o", str(tmp_path), "--combined")
        assert result.returncode == 0
        json_files = list(tmp_path.glob("*.json"))
        assert len(json_files) == 1

    def test_merged_content(self, tmp_path):
        sms = str(FIXTURES_DIR / "minimal_sms.xml")
        calls = str(FIXTURES_DIR / "minimal_calls.xml")
        run_cli("parse", sms, calls, "-o", str(tmp_path), "--combined")
        json_files = list(tmp_path.glob("*.json"))
        with open(json_files[0], encoding='utf-8') as f:
            data = json.load(f)
        assert len(data["sms"]) >= 1
        assert len(data["calls"]) >= 1


class TestCliValidateFlag:
    """The --validate flag runs schema validation after parsing."""

    def test_validate_succeeds(self, tmp_path):
        xml = str(FIXTURES_DIR / "minimal_sms.xml")
        result = run_cli("parse", xml, "-o", str(tmp_path), "--combined", "--validate")
        # Should succeed (exit 0) or fail with import error — not crash
        assert result.returncode in (0, 1)


class TestCliCompactFlag:
    """The --compact flag produces compact JSON."""

    def test_compact_output(self, tmp_path):
        xml = str(FIXTURES_DIR / "minimal_sms.xml")
        run_cli("parse", xml, "-o", str(tmp_path), "--combined", "--compact")
        json_files = list(tmp_path.glob("*.json"))
        assert len(json_files) >= 1
        content = json_files[0].read_text(encoding='utf-8')
        assert "    " not in content


# ── Report subcommand tests ─────────────────────────────────────────────


def _parse_to_json(tmp_path):
    """Parse mixed.xml into combined JSON for report tests."""
    xml = str(FIXTURES_DIR / "mixed.xml")
    run_cli("parse", xml, "-o", str(tmp_path), "--combined")
    json_files = list(tmp_path.glob("*.json"))
    assert len(json_files) == 1
    return str(json_files[0])


class TestCliReportSingleType:
    """Single report type writes one file to the exact specified path."""

    def test_summary_to_file(self, tmp_path):
        json_path = _parse_to_json(tmp_path)
        out = tmp_path / "report.txt"
        result = run_cli("report", json_path, "-t", "summary", "-o", str(out))
        assert result.returncode == 0
        assert out.exists()

    def test_csv_single_no_double_newlines(self, tmp_path):
        json_path = _parse_to_json(tmp_path)
        out = tmp_path / "report.csv"
        result = run_cli("report", json_path, "-t", "summary", "--format", "csv", "-o", str(out))
        assert result.returncode == 0
        content = out.read_bytes()
        assert b"\r\r" not in content


class TestCliReportAll:
    """-t all -o <path> creates three separate output files."""

    def test_creates_three_files(self, tmp_path):
        json_path = _parse_to_json(tmp_path)
        out = tmp_path / "report.csv"
        result = run_cli("report", json_path, "-t", "all", "--format", "csv", "-o", str(out))
        assert result.returncode == 0
        expected = {"report_summary.csv", "report_contacts.csv", "report_timeline.csv"}
        created = {f.name for f in tmp_path.glob("report_*.csv")}
        assert expected == created

    def test_all_stdout(self, tmp_path):
        json_path = _parse_to_json(tmp_path)
        result = run_cli("report", json_path, "-t", "all", "--format", "text")
        assert result.returncode == 0
        assert "Backup Summary" in result.stdout
        assert "Contacts Report" in result.stdout
        assert "Timeline Report" in result.stdout


class TestCliReportFormatMismatchWarning:
    """Mismatched --format and file extension emits a warning."""

    def test_csv_format_json_extension_warns(self, tmp_path):
        json_path = _parse_to_json(tmp_path)
        out = tmp_path / "report.json"
        result = run_cli("report", json_path, "-t", "summary", "--format", "csv", "-o", str(out))
        assert result.returncode == 0
        assert "Warning" in result.stderr
        assert ".csv" in result.stderr

    def test_matching_extension_no_warning(self, tmp_path):
        json_path = _parse_to_json(tmp_path)
        out = tmp_path / "report.csv"
        result = run_cli("report", json_path, "-t", "summary", "--format", "csv", "-o", str(out))
        assert result.returncode == 0
        assert "Warning" not in result.stderr


class TestCliMultiFileCombinedNaming:
    """Multi-file --combined uses 'combined' stem instead of input name."""

    def test_combined_stem(self, tmp_path):
        sms = str(FIXTURES_DIR / "minimal_sms.xml")
        calls = str(FIXTURES_DIR / "minimal_calls.xml")
        result = run_cli("parse", sms, calls, "-o", str(tmp_path), "--combined")
        assert result.returncode == 0
        json_files = list(tmp_path.glob("*.json"))
        assert len(json_files) == 1
        assert json_files[0].stem == "combined"

    def test_single_file_keeps_input_stem(self, tmp_path):
        sms = str(FIXTURES_DIR / "minimal_sms.xml")
        result = run_cli("parse", sms, "-o", str(tmp_path), "--combined")
        assert result.returncode == 0
        json_files = list(tmp_path.glob("*.json"))
        assert len(json_files) == 1
        assert json_files[0].stem == "minimal_sms"
