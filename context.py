from enum import Enum


class ParsingContext(Enum):
    IMPORTS = 0
    UNROLLING = 1
    MEMBERS = 2
    FUNCTION = 3
    INDETERMINATE = 4
    BEFORE = 5
