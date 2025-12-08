from enum import Enum, auto


class Errors(str, Enum):
    SUCCESS = auto()

    TYPE_ERROR = auto()
    WRONG_COMMAND_ERROR = auto()
    DATE_ERROR = auto()

    DB_FAIL = auto()
    DB_DUPLICATE_DAY = auto()
