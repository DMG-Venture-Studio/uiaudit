"""The command line: `uiaudit <noun> <verb> --json`, one command per operation in the catalog."""

import json
import sys
from dataclasses import asdict

from uiaudit import boot
from uiaudit.catalog.index import OPERATIONS
from uiaudit.kernel.envelope import Envelope


def listing() -> list[str]:
    """The commands this surface exposes, one per operation in the catalog."""
    return [name.replace(".", " ") for name in sorted(OPERATIONS)]


def main(argv: list[str] | None = None) -> int:
    """Print what this surface exposes as an envelope; the transport itself is built per slice."""
    boot.build()
    arguments = sys.argv[1:] if argv is None else argv
    print(json.dumps(asdict(Envelope(ok=True, data={"commands": listing(), "arguments": arguments}))))
    return 0
