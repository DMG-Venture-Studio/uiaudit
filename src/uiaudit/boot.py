"""The composition root: builds each adapter once and hands the resources to the catalog."""

from uiaudit.kernel.resources import Resources


def build() -> Resources:
    """Every resource an operation may ask for, built once."""
    return Resources()
