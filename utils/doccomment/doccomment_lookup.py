from dataclasses import dataclass
from pathlib import Path
from typing import Sequence
from utils.data.swift_decl_visitor import SwiftDeclCallableVisitor
import io

from utils.data.swift_decls import SwiftDecl, SwiftDeclWalker
from utils.doccomment.doccomment_block import DoccommentBlock


class DoccommentLookup:
    """
    Performs parsing and lookup of doc comments using `SwiftDecl.origin.path`.
    """

    @dataclass(init=False)
    class _CachedFile:
        path: Path
        doccomments: list[DoccommentBlock]
        doccomment_line_map: dict[int, DoccommentBlock]

        def __init__(self, path, doccomments):
            self.path = path
            self.doccomments = doccomments

            # Populate line cache
            self.doccomment_line_map = dict()
            for comment in self.doccomments:
                for line in range(comment.line, comment.end_line()):
                    self.doccomment_line_map[line] = comment

        def has_comment_on_line(self, line: int):
            return line in self.doccomment_line_map

        def comment_on_line(self, line: int):
            return self.doccomment_line_map.get(line)

    _cached_files: dict[Path, _CachedFile]

    doccomment_patterns: list[str]
    "Note: should be sorted by length in descending order"

    def __init__(self, doccomment_patterns: list[str]) -> None:
        self._cached_files = dict()
        self.doccomment_patterns = sorted(doccomment_patterns, key=len, reverse=True)

    def populate_doc_comments(self, decls: Sequence[SwiftDecl]) -> list[SwiftDecl]:
        "Populates doc comments for a provided sequence of Swift declarations, returning a list of copies of the declarations with doccomments populated."

        results = [decl.copy() for decl in decls]
        self.populate_doc_comments_inplace(results)
        return results

    def populate_doc_comments_inplace(self, decls: Sequence[SwiftDecl]):
        "Populates doc comments for a provided sequence of Swift declarations, modifying each declaration in-place."
        visitor = SwiftDeclCallableVisitor(self._populate)

        walker = SwiftDeclWalker(visitor)

        for decl in decls:
            walker.walk_decl(decl)

    def _populate(self, decl: SwiftDecl):
        decl.doccomment = self._find_doccomment(decl)

    def _fetch_file(self, file_path: Path) -> _CachedFile | None:
        cached_file = self._cached_files.get(file_path)
        if cached_file is not None:
            return cached_file

        if not (file_path.exists() and file_path.is_file()):
            return None

        with open(file_path) as file:
            comments = _split_doccomment_lines(
                file_path, file, self.doccomment_patterns
            )
            cache_file = self._CachedFile(file_path, comments)

            self._cached_files[file_path] = cache_file

            return cache_file

    def _find_doccomment(self, decl: SwiftDecl) -> DoccommentBlock | None:
        # The original node is required for this lookup.
        if decl.original_node is None or decl.origin is None:
            return None

        decl_file_path = decl.origin.file
        decl_line_num = decl.origin.line

        cached_file = self._fetch_file(decl_file_path)

        if cached_file is None:
            return None

        # Attempt to intercept comments that are inline with the declaration
        inline = self._doccomment_for_line(cached_file, decl_line_num)
        if inline is not None:
            return inline.normalize_indentation()

        # Collect all single-line doc comment lines that precede the definition
        # line until we reach a line that is not a doc comment, at which case
        # return the collected doc comment lines.
        collected = []
        for i in reversed(range(decl_line_num)):
            doc = self._doccomment_for_line(cached_file, i)

            if doc is None:
                break

            collected.append(doc)

            # Quit after multi-line doc comments
            if doc.is_multi_lined():
                break

        merged = DoccommentBlock.merge_list(reversed(collected))
        if merged is None:
            return None

        return merged.normalize_indentation()

    def _doccomment_for_line(
        self, cached_file: _CachedFile, line: int
    ) -> DoccommentBlock | None:
        return cached_file.comment_on_line(line)


def _split_doccomment_lines(
    path: Path, text_stream: io.TextIOBase, doccomment_patterns: list[str]
) -> list[DoccommentBlock]:
    """
    Returns a list of doc comments that match a given set of doc comment patterns,
    parsed from the given text stream.

    Returns comments ordered as they where found in the stream.
    """

    def close_current(line: int, column: int, contents: str):
        for pattern in doccomment_patterns:
            if not contents.startswith(pattern):
                continue

            contents = contents[len(pattern) :]

            return DoccommentBlock(
                file=path,
                line=line,
                column=column + len(pattern),
                comment_contents=contents,
                line_count=contents.count("\n") + 1,
            )

        return None

    result: list[DoccommentBlock] = []

    line = 1
    column = 0

    current_line = 0
    current_column = 0
    current_contents = ""

    state_default = 0
    state_line_comment = 1
    state_multi_line_comment = 2
    state_string = 3

    state = state_default

    last_char = ""
    index = 0
    while (next := text_stream.read(1)) != "":
        index += 1
        if next == "\n":
            column = 0
            line += 1
        else:
            column += 1

        if state == state_default:  # Regular JSON structure stream
            if next == '"':
                # Start of string literal
                state = state_string
            elif last_char == "/":
                # Keep recording the indices regardless of whether this is a
                # comment or not to reduce duplication
                current_line = line
                current_column = column

                if next == "/":
                    # Line comment
                    state = state_line_comment
                    current_contents = "//"
                elif next == "*":
                    # Multi-line comment
                    state = state_multi_line_comment
                    current_contents = "/*"
        elif state == state_line_comment:  # Inside line comment
            if next == "\n":
                # End of comment; back to regular JSON stream
                state = state_default

                if new_comment := close_current(
                    current_line, current_column, current_contents
                ):
                    result.append(new_comment)
            else:
                current_contents += next
        elif state == state_multi_line_comment:  # Inside multi-line comment
            if next == "/" and last_char == "*":
                # Explicit end of comment block; back to regular JSON stream
                state = state_default
                current_contents += "*/"

                if new_comment := close_current(
                    current_line, current_column, current_contents
                ):
                    result.append(new_comment)
            else:
                current_contents += next
        elif state == state_string:  # Inside string literal
            if next == '"' and last_char != "\\":  # Escaped string terminator check
                # End of string; back to regular JSON stream
                state = state_default

        last_char = next

    # Finish any existing comment
    if state == state_line_comment or state == state_multi_line_comment:
        close_current(
            current_line,
            current_column,
            current_contents,
        )

    return result
