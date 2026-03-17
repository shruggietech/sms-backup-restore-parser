#!/usr/bin/env python3
"""Build standalone executable for sms-backup-parser.

Usage:
    python scripts/build.py

Requires PyInstaller: pip install pyinstaller
"""

import platform
import subprocess
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DIST_DIR = PROJECT_ROOT / "dist"
SRC_DIR = PROJECT_ROOT / "src"
SCHEMA_FILE = PROJECT_ROOT / "sms-backup-restore.schema.json"
ENTRY_POINT = SRC_DIR / "sms_backup_parser" / "cli.py"


def build():
    system = platform.system().lower()
    exe_name = "sms-backup-parser.exe" if system == "windows" else "sms-backup-parser"

    # Determine the correct path separator for --add-data
    sep = ";" if system == "windows" else ":"

    cmd = [
        sys.executable, "-m", "PyInstaller",
        "--onefile",
        "--name", exe_name.replace(".exe", ""),
        "--distpath", str(DIST_DIR),
        "--workpath", str(PROJECT_ROOT / "build"),
        "--specpath", str(PROJECT_ROOT),
        f"--add-data={SCHEMA_FILE}{sep}.",
        "--paths", str(SRC_DIR),
        "--clean",
        str(ENTRY_POINT),
    ]

    print(f"Building {exe_name} for {platform.system()} {platform.machine()}...")
    print(f"Command: {' '.join(cmd)}")

    result = subprocess.run(cmd)

    if result.returncode != 0:
        print(f"Build failed with exit code {result.returncode}", file=sys.stderr)
        sys.exit(1)

    output_path = DIST_DIR / exe_name
    if output_path.exists():
        size_mb = output_path.stat().st_size / (1024 * 1024)
        print(f"\nBuild successful: {output_path} ({size_mb:.1f} MB)")
    else:
        print(f"Build completed but output not found at {output_path}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    build()
