"""Every built operation by name: what it is, who may call it, where it is exposed."""

from dataclasses import dataclass
from typing import Literal


@dataclass(frozen=True)
class Operation:
    """One operation's declaration; the function itself lives in its noun's ops."""

    name: str
    summary: str
    grant: str
    effect: Literal["read", "write", "spend", "external"]
    resources: tuple[str, ...] = ()
    surfaces: tuple[str, ...] = ("cli", "http", "mcp")


# An operation enters the catalog when its slice is built; project-spec.toml holds the plan.
OPERATIONS: dict[str, Operation] = {}
