from enum import Enum
from os import PathLike
import json
from pathlib import Path

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
    class CharStream:
        def __init__(self, buffer: str):
            self.buffer = buffer
            self.index = 0
        
        def isEoF(self):
            "Returns `True` if the current stream position is past the end of the available string."
            return self.index >= len(self.buffer)
        
        def isEoF_l(self, length: int):
            "Returns `True` if the current stream position + `length` is past the end of the available string."
            return (self.index + length) >= len(self.buffer)

        def _checkEoF(self):
            assert not self.isEoF(), "Attempted to read past end of the buffer!"
        
        def _checkEoF_l(self, length: int):
            assert not self.isEoF_l(length), "Attempted to read past end of the buffer!"
        
        def advance(self):
            "Advances the stream's position by 1."
            self._checkEoF()
            self.index += 1
            
        def advance_l(self, length):
            "Advances the stream's position by `length`."
            self._checkEoF_l(length)
            self.index += length
        
        def peek(self) -> str:
            "Returns the next character in the stream, but does not change its position."
            self._checkEoF()
            return self.buffer[self.index]
        
        def peek_l(self, length: int) -> str:
            "Returns the next `length` characters in the stream, but does not change its position."
            assert length >= 0, "Attempted to peek_l with negative length!"
            self._checkEoF_l(length)
            return self.buffer[(self.index):(self.index + length)]
        
        def next(self) -> str:
            "Returns the next character in the stream, advancing its position by 1."
            char = self.peek()
            self.advance()
            return char
        
        def next_l(self, length: int) -> str:
            "Returns the next `length` characters in the stream, advancing its position by `length`."
            result = self.peek_l(length)
            self.advance_l(length)
            return result
        
        def is_next(self, char: str) -> bool:
            "Returns `True` if the buffer has a given string at the current position. If len(char) leads to EoF but the current position is not EoF, `False` is returned."
            length = len(char)
            if length == 1:
                return self.peek() == char
            
            self._checkEoF()
            if self.isEoF_l(length):
                return False
            
            return self.peek_l(length) == char
        
        def advance_if_next(self, char: str) -> bool:
            "Advances from the current position in the stream iff `self.is_next(char) == True`"
            if not self.is_next(char):
                return False
            
            self.advance_l(len(char))
            return True
    
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

    while not stream.isEoF():
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
