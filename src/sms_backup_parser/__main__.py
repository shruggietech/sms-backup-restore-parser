"""Allow running as python -m sms_backup_parser."""

import sys

from sms_backup_parser.cli import main

if __name__ == "__main__":
    sys.exit(main())
