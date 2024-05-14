from enum import Enum


class CDeclKind(Enum):
    """
    Represents a kind of C declaration.
    """

    NONE = 0
    "No declaration associated."

    ENUM = 1
    "A C-style enum declaration."
    ENUM_CASE = 2
    "A C-style enum value declaration."
    STRUCT = 3
    "A C-style struct declaration."
    FUNC = 4
    "A C-style function declaration."
