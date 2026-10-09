"""The catalog holds only operations the spec declares."""

import tomllib
from pathlib import Path

from uiaudit.catalog.index import OPERATIONS, Operation

SPEC = Path(__file__).resolve().parents[1] / "project-spec.toml"


def test_every_catalog_operation_is_declared_in_the_spec():
    nouns = tomllib.loads(SPEC.read_text())["nouns"]
    declared = {op for noun in nouns for op in noun["operations"]}
    assert set(OPERATIONS) <= declared


def test_the_default_surfaces_of_an_operation_are_the_surfaces_the_spec_enables():
    enabled = {name for name, on in tomllib.loads(SPEC.read_text())["surfaces"].items() if on}
    assert set(Operation("x.y", "", "x.y", "read").surfaces) == enabled
