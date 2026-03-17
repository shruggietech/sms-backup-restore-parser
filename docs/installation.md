# Installation

## Pre-built Binaries

Standalone executables for Windows and Ubuntu are available on [GitHub Releases](https://github.com/ShruggieTech/sms-backup-restore-parser/releases). These require no Python installation.

| Platform | File | Notes |
|----------|------|-------|
| Windows | `sms-backup-parser.exe` | Windows 10+ |
| Ubuntu | `sms-backup-parser` | Ubuntu 22.04+, mark as executable with `chmod +x` |

Download the binary for your platform, place it somewhere on your `PATH`, and run it directly:

```bash
# Windows
sms-backup-parser.exe parse backup.xml

# Linux
./sms-backup-parser parse backup.xml
```

## Install from Source

Requires Python 3.12 or later.

```bash
pip install -e .
```

This installs the `sms-backup-parser` command and the `sms_backup_parser` Python package.

To include optional schema validation support:

```bash
pip install -e ".[validate]"
```

## Development Setup

Clone the repository and create a virtual environment:

```bash
git clone https://github.com/ShruggieTech/sms-backup-restore-parser.git
cd sms-backup-restore-parser

python -m venv .venv
source .venv/bin/activate   # .venv\Scripts\activate on Windows

pip install -e ".[dev]"
```

To install the documentation toolchain (MkDocs and Material for MkDocs):

```bash
pip install -e ".[docs]"
```

### Running Tests

```bash
pytest tests/
```

### Running the Parser (dev mode)

```bash
python -m sms_backup_parser parse backup.xml -o ./output
```

### Building Executables

Build scripts are located in `scripts/`. See those files for platform-specific build instructions.
