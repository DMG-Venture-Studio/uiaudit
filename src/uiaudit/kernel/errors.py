"""The errors every package shares; a noun's own errors live in its model."""


class Refused(Exception):
    """The caller may not do this; the message says why and what to send instead."""


class NotFound(Exception):
    """No record has the id the caller gave."""
