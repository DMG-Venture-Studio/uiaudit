"""Every operation appears on every surface it declares, and no surface exposes anything else."""

import tomllib
from pathlib import Path

from uiaudit.catalog.index import OPERATIONS, on_surface
from uiaudit.surfaces import cli, http, mcp

SPEC = Path(__file__).resolve().parents[1] / "project-spec.toml"
PROJECTIONS = {
    "cli": lambda name: name.replace(".", " ") in cli.listing(),
    "http": lambda name: "/" + name.replace(".", "/") in http.listing(),
    "mcp": lambda name: name.replace(".", "_") in mcp.listing(),
}


def test_every_operation_is_on_every_surface_it_declares():
    missing = [
        f"{name} declares {surface} but the {surface} surface does not expose it"
        for name, operation in OPERATIONS.items()
        for surface in operation.surfaces
        if not PROJECTIONS[surface](name)
    ]
    assert missing == []


def test_no_surface_exposes_an_operation_that_did_not_declare_it():
    for surface, listing in (("cli", cli.listing), ("http", http.listing), ("mcp", mcp.listing)):
        assert len(listing()) == len(on_surface(surface)), f"the {surface} surface exposes more than declared"


def test_the_mcp_entry_point_is_built_or_is_the_spec_first_operation():
    first = tomllib.loads(SPEC.read_text())["project"]["first_operation"].replace(".", "_")
    assert mcp.ENTRY_POINT in mcp.listing() or first == mcp.ENTRY_POINT
    assert mcp.ENTRY_POINT in mcp.INSTRUCTIONS
