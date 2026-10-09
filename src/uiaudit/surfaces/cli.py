"""The command line: `uiaudit <noun> <verb> --json`, one command per operation in the catalog."""

import json
import sys
from dataclasses import asdict

from uiaudit import boot
from uiaudit.catalog.index import on_surface
from uiaudit.kernel.envelope import Envelope

USAGE = "usage: uiaudit <noun> <verb> [--json]"


def listing() -> list[str]:
    """The commands this surface exposes, one per operation in the catalog."""
    return [operation.name.replace(".", " ") for operation in on_surface("cli")]


def help_text() -> str:
    """The help a person or an agent reads: usage, then one line per command with its summary."""
    commands = [
        f"  {command:<28} {operation.summary}"
        for command, operation in zip(listing(), on_surface("cli"), strict=True)
    ]
    footer = "Data on stdout as the versioned envelope, diagnostics on stderr; a nonzero exit is an error."
    return "\n".join([USAGE, "", "commands:", *commands, "", footer]) + "\n"


def main(argv: list[str] | None = None) -> int:
    """Print what this surface exposes as an envelope; the transport itself is built per slice."""
    boot.build()
    arguments = sys.argv[1:] if argv is None else argv
    print(json.dumps(asdict(Envelope(ok=True, data={"commands": listing(), "arguments": arguments}))))
    return 0
