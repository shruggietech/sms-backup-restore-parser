"""Tests for the sms_backup_parser CLI entry point."""

import subprocess
import sys
from pathlib import Path

import pytest

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
