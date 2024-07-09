from typing import Callable, Iterable, TextIO, TypeVar
from contextlib import contextmanager

T = TypeVar("T")


class SyntaxStream:
    """Class used to generate Swift syntax strings."""

    def __init__(self, destination: TextIO):
        self.destination = destination
        self.indent_depth = 0

    def write(self, text: str):
        self.destination.write(text)

    def write_then_line(self, text: str = ""):
        """Writes a given string of text and output a line break at the end."""
        self.write(f"{text}\n")

    def indent_str(self) -> str:
        return "    " * self.indent_depth

    def line(self, text: str = ""):
        """
        Writes an indented line of text with contents of `text` before emitting
        a newline.
        """
        self.pre_line()
        self.write_then_line(text)

    def pre_line(self):
        """Emits the indentation for a line."""
        self.write(f"{self.indent_str()}")

    def indent(self):
        self.indent_depth += 1

    def unindent(self):
        self.indent_depth -= 1

    def with_separator(
        self, sep: str, items: Iterable[T], writer: Callable[["SyntaxStream", T], None]
    ):
        """
        Returns a callable that receives a SyntaxStream, and from the second item
        onwards also prepends the stream with `sep` automatically.

        ```python
        listElements = [<item 1>, <item 2>, <item 3>]
        stream.with_separator(
            " & ",
            listElements,
            lambda stream, item: item.write(stream)
        )
        ```

        Produces the stream:

        ```
        <item 1> & <item 2> & <item 3>
        ```
        """
        count = 0
        for item in items:
            if count > 0:
                self.write(sep)

            writer(self, item)

            count += 1

    @contextmanager
    def block(self, line: str):
        """
        Starts a block context by emitting an indented line with contents `line`,
        followed by a newline, then allowing a block with indented syntax to be
        generated via `yield` before de-indenting and emitting a close brace.

        ```
        with stream.block("if true {"):
            stream.line("print()")
        ```

        Produces:

        ```swift
        if true {
            print()
        }
        ```
        """
        self.line(line)
        self.indent()

        yield

        self.unindent()
        self.line("}")

    @contextmanager
    def inline_block(self, line: str, close_brace: str = "}"):
        """
        Starts a block context by emitting `line`, followed by a newline, then
        allowing a block with indented syntax to be generated via `yield` before
        de-indenting and emitting a close brace.

        ```
        stream.pre_line()
        stream.write("let list = ")
        with stream.block("[", close_brace="]"):
            stream.line("0, 1, 2")
        ```

        Produces:

        ```swift
        let list = [
            0, 1, 2
        ]
        ```
        """
        self.write_then_line(line)
        self.indent()

        yield

        self.unindent()
        self.line(close_brace)
