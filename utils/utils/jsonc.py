if __name__ == "__main__":
    import sys
    import pathlib

    sys.path.insert(0, str(pathlib.Path(__file__).joinpath("../../../").resolve()))

from enum import Enum
from os import PathLike
import json
from pathlib import Path
import io


def jsonc_load(path: PathLike):
    """Loads the contents of the given JSONC string buffer as a JSON with `json.loads`"""
    with open(path, "r") as file:
        return jsonc_loads(file.read())


def jsonc_loads(string: str | bytes | bytearray):
    """Loads the contents of the given JSONC string buffer as a JSON with `json.loads`"""
    _string: str
    if isinstance(string, str):
        _string = string
    elif isinstance(string, bytes):
        _string = str(string)
    else:
        _string = str(string)

    return json.loads(jsonc_strip_comments(_string))


def jsonc_strip_comments(source: str | Path) -> str:
    """Strips C-style comments from a given JSON string or JSON file's contents, returning a string capable of being parsed with `json.loads(<str>)`"""

    if isinstance(source, Path):
        with open(source, "r") as f:
            return _jsonc_strip_comments(f)
    else:
        stream = io.StringIO(source)
        return _jsonc_strip_comments(stream)


def _jsonc_strip_comments(stream: io.TextIOBase) -> str:
    class State(Enum):
        DEFAULT = 0
        LINE_COMMENT = 1
        MULTI_LINE_COMMENT = 2
        STRING = 3

    state = State.DEFAULT

    new_json = ""
    last_char = ""
    while (next := stream.read(1)) != "":
        match state:
            case State.DEFAULT:  # Regular JSON structure stream
                if next == '"':
                    # Start of string literal
                    state = State.STRING
                    new_json += '"'
                elif last_char == "/" and next == "/":
                    # Start of line comment
                    state = State.LINE_COMMENT
                    new_json += " "  # Insert dummy placeholders for line/column keeping purposes
                elif last_char == "/" and next == "*":
                    # Start of multi-line comment
                    state = State.MULTI_LINE_COMMENT
                    new_json += " "
                elif next == "/":
                    # Withhold on // so we can detect comments without parsing the forward slash as a JSON character
                    pass
                else:
                    # Regular JSON structure character
                    if last_char == "/":
                        new_json += last_char
                    new_json += next
            case State.LINE_COMMENT:  # Inside line comment
                if next == "\n":
                    # End of comment; back to regular JSON stream
                    state = State.DEFAULT
                    new_json += "\n"
                else:
                    new_json += " "
            case State.MULTI_LINE_COMMENT:  # Inside multi-line comment
                if next == "/" and last_char == "*":
                    # Explicit end of comment block; back to regular JSON stream
                    state = State.DEFAULT
                    new_json += " "
                    next = " "  # Prevent re-capturing final forward slash
                else:
                    new_json += "\n" if next == "\n" else " "
            case State.STRING:  # Inside string literal
                new_json += next
                if next == '"' and last_char != "\\":  # Escaped string terminator check
                    # End of string; back to regular JSON stream
                    state = State.DEFAULT

        last_char = next

    return new_json


if __name__ == "__main__":
    testJson = """
    {
        "field0": 0,
        // Line comment
        "field1": "a /* commented // */ string",
        "fie\\"ld2":
            /* Multi-lined comment
            */ "abc"
    }
    """
    print(testJson)
    print(jsonc_strip_comments(testJson))
