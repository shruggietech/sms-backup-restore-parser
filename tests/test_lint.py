"""Lint test — runs ruff against the codebase to catch style and correctness issues."""

import subprocess
import sys


def test_ruff_lint():
    """All source and test files pass ruff linting."""
    result = subprocess.run(
        [sys.executable, "-m", "ruff", "check", "src/", "tests/"],
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, f"ruff found lint errors:\n{result.stdout}"
