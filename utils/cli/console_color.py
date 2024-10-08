from enum import Enum, unique
from functools import reduce
from typing import Any


@unique
class ConsoleStyle(str, Enum):
    NORMAL = "normal"
    BOLD = "bold"
    FAINT = "faint"
    UNDERLINE = "underline"


@unique
class ConsoleColor(str, Enum):
    NORMAL = "normal"
    BLACK = "black"
    RED = "red"
    GREEN = "green"
    YELLOW = "yellow"
    BLUE = "blue"
    MAGENTA = "magenta"
    CYAN = "cyan"
    WHITE = "white"

    def __call__(self, *args: Any, **kwds: Any) -> Any:
        if bold := kwds.get("bold"):
            return colored(bold, color=self, style=ConsoleStyle.BOLD)
        if underlined := kwds.get("underlined"):
            return colored(underlined, color=self, style=ConsoleStyle.UNDERLINE)

        if len(args) > 0:
            return colored(*args, color=self)
        else:
            return ""


def joined(text: tuple[Any, ...]) -> str:
    return reduce(lambda x, y: f"{x} {y}", text[1:], text[0])


def colored(
    *text: Any, color: ConsoleColor | None = None, style: ConsoleStyle | None = None
) -> str:
    return f"{color_foreground_ascii(color, style)}{joined(text)}{color_foreground_ascii(ConsoleColor.NORMAL)}"


def color_foreground_ascii(
    color: ConsoleColor | None = None, style: ConsoleStyle | None = None
) -> str:
    joined = ";".join(
        str(x)
        for x in [
            style_code(style),
            color_foreground_code(color),
        ]
        if x != 0
    )

    if joined == "":
        joined = "0"

    return f"\u001b[{joined}m"


def color_background_ascii(
    color: ConsoleColor | None = None, style: ConsoleStyle | None = None
) -> str:
    joined = ";".join(
        str(x)
        for x in [
            style_code(style),
            color_background_code(color),
        ]
        if x != 0
    )

    if joined == "":
        joined = "0"

    return f"\u001b[{joined}m"


def style_code(style: ConsoleStyle | None = None) -> int:
    match style:
        case None:
            return 0
        case ConsoleStyle.NORMAL:
            return 0
        case ConsoleStyle.BOLD:
            return 1
        case ConsoleStyle.FAINT:
            return 2
        case ConsoleStyle.UNDERLINE:
            return 4


def color_foreground_code(color: ConsoleColor | None) -> int:
    match color:
        case None | ConsoleColor.NORMAL:
            return 0
        case ConsoleColor.BLACK:
            return 30
        case ConsoleColor.RED:
            return 31
        case ConsoleColor.GREEN:
            return 32
        case ConsoleColor.YELLOW:
            return 33
        case ConsoleColor.BLUE:
            return 34
        case ConsoleColor.MAGENTA:
            return 35
        case ConsoleColor.CYAN:
            return 36
        case ConsoleColor.WHITE:
            return 37


def color_background_code(color: ConsoleColor | None) -> int:
    match color:
        case None | ConsoleColor.NORMAL:
            return 0
        case ConsoleColor.BLACK:
            return 40
        case ConsoleColor.RED:
            return 41
        case ConsoleColor.GREEN:
            return 42
        case ConsoleColor.YELLOW:
            return 43
        case ConsoleColor.BLUE:
            return 44
        case ConsoleColor.MAGENTA:
            return 45
        case ConsoleColor.CYAN:
            return 46
        case ConsoleColor.WHITE:
            return 47
