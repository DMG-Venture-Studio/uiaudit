"""The catalog holds only operations the spec declares."""

import tomllib
from pathlib import Path

from uiaudit.catalog.index import OPERATIONS

SPEC = Path(__file__).resolve().parents[1] / "project-spec.toml"


def test_every_catalog_operation_is_declared_in_the_spec():
    nouns = tomllib.loads(SPEC.read_text())["nouns"]
    declared = {op for noun in nouns for op in noun["operations"]}
    assert set(OPERATIONS) <= declared
