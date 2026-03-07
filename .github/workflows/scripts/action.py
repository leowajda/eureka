from __future__ import annotations

from enum import Enum, unique


@unique
class Action(str, Enum):
    """Represents the CI action associated with a solution file change.

    Members are compared case-insensitively and support fuzzy substring
    matching via :py:meth:`_missing_`, so raw GitHub Actions event strings
    such as ``"added_files"`` correctly resolve to :attr:`ADD`.
    """

    ADD = "add"
    UPDATE = "update"
    REMOVE = "remove"
    UNDEFINED = "undefined"

    @classmethod
    def _missing_(cls, value: object) -> Action:
        """Resolve *value* to the best-matching member, or :attr:`UNDEFINED`.

        ``Enum._missing_`` is invoked whenever ``Action(value)`` is called
        with a value that does not exactly match any member.  The contract
        from :pep:`435` allows *value* to be of *any* type (including
        ``None``), so a type guard is applied before any string operations.

        The match is a case-insensitive substring check: a member is
        returned when its canonical value appears anywhere inside the
        normalised *value* string.  This lets caller-supplied strings such
        as ``"added_files"`` resolve to :attr:`ADD` without requiring an
        exact match.

        Args:
            value: The raw value passed to ``Action(...)``.  May be
                ``None`` or a non-string type when the enum machinery
                calls this hook after a failed direct lookup.

        Returns:
            The first member whose value is a substring of the normalised
            *value*, or :attr:`Action.UNDEFINED` when no member matches or
            *value* is not a string.
        """
        if not isinstance(value, str):
            return cls.UNDEFINED

        normalised = value.lower()
        for member in cls:
            if member.value in normalised:
                return member

        return cls.UNDEFINED
