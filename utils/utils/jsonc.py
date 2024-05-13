from enum import Enum
from os import PathLike
import json
from pathlib import Path

from utils.text.char_stream import CharStream

def jsonc_load(path: PathLike):
    "Loads the contents of the given JSONC string buffer as a JSON with `json.loads`"
    with open(path, 'r') as file:
        return jsonc_loads(file.read())

def jsonc_loads(string: str | bytes | bytearray):
    "Loads the contents of the given JSONC string buffer as a JSON with `json.loads`"
    _string: str
    if isinstance(string, str):
        _string = string
    elif isinstance(string, bytes):
        _string = str(string)
    elif isinstance(string, bytearray):
        _string = str(string)
    
    return json.loads(jsonc_strip_comments(_string))

def jsonc_strip_comments(source: str | Path) -> str:
    "Strips C-style comments from a given JSON string or JSON file's contents, returning a string capable of being parsed with `json.loads(<str>)`"
    
    class State(Enum):
        DEFAULT = 0
        LINE_COMMENT = 1
        MULTI_LINE_COMMENT = 2
        STRING = 3

    #

    string: str
    if isinstance(source, Path):
        with open(source, 'r') as f:
            string = f.read()
    else:
        string = source

    state = State.DEFAULT

    stream = CharStream(string)
    new_json = ""

    while not stream.is_eof():
        match state:
            case State.DEFAULT:  # Regular JSON structure stream
                if stream.advance_if_next('"'):
                    # Start of string literal
                    state = State.STRING
                    new_json += '"'
                elif stream.advance_if_next("//"):
                    # Start of line comment
                    state = State.LINE_COMMENT
                    new_json += "  "  # Insert dummy placeholders for line/column keeping purposes
                elif stream.advance_if_next("/*"):
                    # Start of multi-line comment
                    state = State.MULTI_LINE_COMMENT
                    new_json += "  "
                else:
                    # Regular JSON structure character
                    new_json += stream.next()
            case State.LINE_COMMENT:  # Inside line comment
                if stream.advance_if_next("\n"):
                    # End of comment; back to regular JSON stream
                    state = State.DEFAULT
                    new_json += "\n"
                else:
                    stream.advance()
                    new_json += " "
            case State.MULTI_LINE_COMMENT:  # Inside multi-line comment
                if stream.advance_if_next("*/"):
                    # Explicit end of comment block; back to regular JSON stream
                    state = State.DEFAULT
                    new_json += "  "
                else:
                    stream.advance()
                    new_json += " "
            case State.STRING:  # Inside string literal
                if stream.advance_if_next(r'\"'):
                    # Escaped string terminator; continue reading as a string still
                    new_json += r'\"'
                elif stream.advance_if_next('"'):
                    # End of string; back to regular JSON stream
                    state = State.DEFAULT
                    new_json += '"'
                else:
                    # String contents
                    new_json += stream.next()

    return new_json
