"""The MCP surface: one tool per operation an agent may call, generated from the catalog."""

import json
import sys
from dataclasses import asdict

from fastmcp import FastMCP

from uiaudit import boot
from uiaudit.catalog.index import Operation, on_surface
from uiaudit.kernel.envelope import Envelope

# What a cold client receives on connect, and nothing else: the purpose, the entry point, one thing
# the server is not for. Held in a constant so the static legibility probe can read it.
ENTRY_POINT = "run_start"
INSTRUCTIONS = (
    "uiaudit audits a web app's UI: it captures each route, state, viewport and theme cell, runs "
    "accessibility checks on it, and turns the findings into a fix plan a coding agent can execute. "
    f"Start with {ENTRY_POINT} to capture a cell; run_show reads a run back. "
    "It is not for triage: only a person accepts or rejects a finding, never a caller of this server."
)


def tool_name(operation: Operation) -> str:
    """The tool an operation becomes: `<noun>_<verb>`."""
    return operation.name.replace(".", "_")


def listing() -> list[str]:
    """The tools this surface exposes, one per operation in the catalog."""
    return [tool_name(operation) for operation in on_surface("mcp")]


def tool_list() -> dict[str, object]:
    """What crosses the wire: the instructions and every tool with its summary, effect and grant."""
    tools = [
        {
            "name": tool_name(operation),
            "description": operation.summary,
            "effect": operation.effect,
            "grant": operation.grant,
        }
        for operation in on_surface("mcp")
    ]
    return {"instructions": INSTRUCTIONS, "entry_point": ENTRY_POINT, "tools": tools}


def server() -> FastMCP:
    """The server a client connects to, carrying the instructions; tools join it slice by slice."""
    return FastMCP(name="uiaudit", instructions=INSTRUCTIONS)


def main(argv: list[str] | None = None) -> int:
    """Print what this surface exposes as an envelope; the transport itself is built per slice."""
    boot.build()
    arguments = sys.argv[1:] if argv is None else argv
    print(json.dumps(asdict(Envelope(ok=True, data={"tools": listing(), "arguments": arguments}))))
    return 0
