from enum import Enum, unique


@unique
class Action(str, Enum):
    ADD = "add"
    UPDATE = "update"
    REMOVE = "remove"
    UNDEFINED = "undefined"

    @classmethod
    def _missing_(cls, value: str):
        value = value.lower()
        for member in cls:
            if member.value in value:
                return member
        return Action.UNDEFINED
