"""The one result shape every surface returns: data, or an error and the next step."""

from dataclasses import dataclass, field


@dataclass(frozen=True)
class Envelope:
    """A versioned result: data on success, or the error and the call that would fix it."""

    ok: bool
    data: dict[str, object] = field(default_factory=dict)
    error: str | None = None
    next_step: str | None = None
    version: int = 1
