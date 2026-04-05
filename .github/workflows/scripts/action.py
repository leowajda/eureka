from __future__ import annotations

from enum import Enum, unique


@unique
class Action(str, Enum):
    ADD = "add"
    UPDATE = "update"
    REMOVE = "remove"
