"""The finding's records and its own errors."""

from dataclasses import dataclass


@dataclass(frozen=True)
class Finding:
    """One problem in one cell, with its recommendation, triage status and identity across runs."""

    key: str
