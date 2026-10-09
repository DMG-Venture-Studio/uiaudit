"""`python -m uiaudit`: the cli surface."""

import sys

from uiaudit.surfaces import cli

sys.exit(cli.main(sys.argv[1:]))
