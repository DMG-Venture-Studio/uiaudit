"""The run's records and its own errors."""

from dataclasses import dataclass


@dataclass(frozen=True)
class Run:
    """One capture of the route, state, viewport and theme matrix, and cell-by-cell comparison across runs."""

    key: str
