"""Top-level module execution entry point (`python -m rocky`)."""

import sys
from rocky.ui.cli import main

if __name__ == "__main__":
    sys.exit(main())