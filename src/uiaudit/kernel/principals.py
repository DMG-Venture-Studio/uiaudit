"""Who is calling, and which operation grants they hold."""

from dataclasses import dataclass


@dataclass(frozen=True)
class Principal:
    """A caller (a person, an agent or a schedule) and the grants it holds."""

    name: str
    grants: frozenset[str]

    def may(self, grant: str) -> bool:
        """Whether this principal holds the grant."""
        return grant in self.grants
