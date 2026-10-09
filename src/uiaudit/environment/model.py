"""The environment's records and its own errors."""

from dataclasses import dataclass


@dataclass(frozen=True)
class Environment:
    """An app under audit in one environment, local or staging: its config, stored sign-in and health."""

    key: str
