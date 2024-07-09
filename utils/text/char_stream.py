class UncheckedCharStream:
    """A character stream from a string that doesn't make checks for EOF on accesses."""

    def __init__(self, buffer: str):
        self.buffer = buffer
        self.index = 0
        self.length = len(buffer)

    def is_eof(self):
        """Returns `True` if the current stream position is past the end of the available string."""
        return self.index >= self.length

    def is_eof_l(self, length: int):
        """Returns `True` if the current stream position + `length` is past the end of the available string."""
        return (self.index + length) >= self.length

    def advance(self):
        """Advances the stream's position by 1."""
        self.index += 1

    def advance_l(self, length):
        """Advances the stream's position by `length`."""
        self.index += length

    def peek(self, offset=1) -> str:
        """Returns the next character in the stream from the current position + offset, but does not change its position."""
        return self.buffer[self.index + (offset - 1)]

    def peek_l(self, length: int) -> str:
        """Returns the next `length` characters in the stream, but does not change its position."""
        return self.buffer[self.index: (self.index + length)]

    def next(self) -> str:
        """Returns the next character in the stream, advancing its position by 1."""
        self.index += 1
        return self.buffer[self.index - 1]

    def next_l(self, length: int) -> str:
        """Returns the next `length` characters in the stream, advancing its position by `length`."""
        result = self.peek_l(length)
        self.advance_l(length)
        return result

    def is_next(self, char: str) -> bool:
        """Returns `True` if the buffer has a given string at the current position. If len(char) leads to EoF but the current position is not EoF, `False` is returned."""
        length = len(char)
        if length == 1:
            return self.peek() == char

        return self.peek_l(length) == char

    def advance_if_next(self, char: str) -> bool:
        """Advances from the current position in the stream iff `self.is_next(char) == True`"""
        if not self.is_next(char):
            return False

        self.advance_l(len(char))
        return True


class CharStream(UncheckedCharStream):
    """A variant of `UncheckedCharStream` that performs EOF checks by default."""

    def _check_eof(self, offset=1):
        assert (
            not (self.index + offset - 1) >= self.length
        ), "Attempted to read past end of the buffer!"

    def _check_eof_l(self, length: int):
        assert not self.is_eof_l(length), "Attempted to read past end of the buffer!"

    def advance(self):
        """Advances the stream's position by 1."""
        self._check_eof()
        self.index += 1

    def advance_l(self, length):
        """Advances the stream's position by `length`."""
        self._check_eof_l(length)
        self.index += length

    def peek(self, offset=1) -> str:
        """Returns the next character in the stream from the current position + offset, but does not change its position."""
        self._check_eof(offset)
        return self.buffer[self.index + (offset - 1)]

    def peek_l(self, length: int) -> str:
        """Returns the next `length` characters in the stream, but does not change its position."""
        assert length >= 0, "Attempted to peek_l with negative length!"
        self._check_eof_l(length)
        return self.buffer[self.index: (self.index + length)]

    def is_next(self, char: str) -> bool:
        """Returns `True` if the buffer has a given string at the current position. If len(char) leads to EoF but the current position is not EoF, `False` is returned."""
        length = len(char)
        if length == 1:
            return self.peek() == char

        self._check_eof()
        if self.is_eof_l(length):
            return False

        return self.peek_l(length) == char
