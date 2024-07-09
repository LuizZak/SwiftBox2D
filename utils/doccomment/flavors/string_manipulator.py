import re


class StringManipulator:
    """Manipulates subsections of strings by extending an index range into buffer before replacing the entire selected range with a substitution."""

    def __init__(self, buffer: str, index: int):
        self.__buffer = buffer
        self.__index = index
        self.__length = 0  # Length of selection
        self.__whitespace_regex = re.compile(r"\s+")

    def get_buffer(self) -> str:
        return self.__buffer

    def start(self) -> int:
        """Returns the start index of the current selection."""
        return self.__index

    def end(self) -> int:
        """Returns the end index of the current selection."""
        return self.__index + self.__length

    def get_range(self) -> range:
        return range(self.start(), self.end())

    # MARK: Extending selection

    def extend_word(self):
        """Extends the current selection by a regex word (`\\w`). Nothing is done if a word cannot be matched at the current range's end point."""
        self.extend(r"\w+")

    def extend_to_newline(self):
        """Extends the current selection until a newline is found. Nothing is done if no newline exists from the current range's end point."""
        self.extend_to(self.__buffer.find("\n", self.end()) + 1)

    def extend_whitespace(self):
        """Extends the current selection past any whitespace available at the current selection end."""
        if match := self.__whitespace_regex.match(self.__buffer, self.end()):
            self.extend_to(match.end())

    def extend_length(self, ext: int):
        """Extends the current selection by a given length."""
        self.__length += ext

    def extend_to(self, end: int):
        """Extends the selection to a specified absolute index into the buffer. If `end` is greater than the current start index, nothing is done."""
        if end < self.__index:
            return

        self.__length = end - self.__index

    def extend(self, pattern: re.Pattern | str) -> str | None:
        """Extends the current selection via regex. Returns the string that resulted from the pattern that was applied, or None, if no match was found at `self.end()`."""
        if isinstance(pattern, str):
            pattern = re.compile(pattern)

        if match := pattern.match(self.__buffer, self.end()):
            self.extend_to(match.end())
            return match.group()

        return None

    # MARK: String operations

    def remove(self):
        """
        Removes the section of the buffer's range represented by `get_range()`.
        Resets the length to 0 in the process.
        """
        range = self.get_range()

        new_buffer = self.__buffer[0 : range.start]
        new_buffer += self.__buffer[range.stop :]
        self.__length = 0
        self.__buffer = new_buffer

    def replace(self, rep: str | None):
        """
        Replaces the current range (`get_range()`) with a given replacement string, resetting the range length to 0 in the process. The current index remains the same.
        If `rep` is `None`, the call is a noop and nothing is changed.
        """
        if rep is None:
            return

        range = self.get_range()

        new_buffer = self.__buffer[0 : range.start]
        new_buffer += rep
        new_buffer += self.__buffer[range.stop :]
        self.__length = 0
        self.__buffer = new_buffer
