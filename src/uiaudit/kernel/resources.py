"""The protocols operations ask for; boot builds the adapters that implement them."""

from dataclasses import dataclass
from typing import Protocol


class Browser(Protocol):
    """Drives Chromium to reach each state and capture screenshots, element boxes and computed styles."""


class AccessibilityScanner(Protocol):
    """Runs axe-core on a captured page and returns its raw results."""


class ImageKit(Protocol):
    """Draws finding boxes, makes thumbnails and computes diff images."""


class ReviewViews(Protocol):
    """Builds the review UI views served inline in Claude, in the local browser and as a static report."""


@dataclass(frozen=True)
class Resources:
    """What boot built; the catalog hands each operation only the resources it names."""
