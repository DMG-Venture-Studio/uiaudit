"""The regression_test's records and its own errors."""

from dataclasses import dataclass


@dataclass(frozen=True)
class RegressionTest:
    """A generated test in the audited repo that fails if a closed finding comes back."""

    key: str
