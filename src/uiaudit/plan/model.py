"""The plan's records and its own errors."""

from dataclasses import dataclass


@dataclass(frozen=True)
class Plan:
    """The task plan built from accepted findings that a coding agent executes in the audited repo."""

    key: str
