"""Allow `python -m code_music` to invoke the CLI."""

import sys

from .cli import main

sys.exit(main())
