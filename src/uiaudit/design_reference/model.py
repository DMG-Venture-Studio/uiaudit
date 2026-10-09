"""The design_reference's records and its own errors."""

from dataclasses import dataclass


@dataclass(frozen=True)
class DesignReference:
    """Optional design tokens and reference screens for the audited app, and the check of captured styles.

    The check compares the styles a run captured against the reference.
    """

    key: str
