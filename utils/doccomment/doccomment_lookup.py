from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from typing import Sequence
from utils.data.swift_decl_visitor import SwiftDeclCallableVisitor

from utils.data.swift_decls import SwiftDecl, SwiftDeclWalker
from utils.doccomment.doccomment_block import DoccommentBlock
from utils.text.char_stream import CharStream

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
            comments = _split_doccomment_lines(file_path, file.read(), self.doccomment_patterns)
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

    def _doccomment_for_line(self, cached_file: _CachedFile, line: int) -> DoccommentBlock | None:
        return cached_file.comment_on_line(line)


def _split_doccomment_lines(path: Path, text_file: str, doccomment_patterns: list[str]) -> list[DoccommentBlock]:
    """
    Returns a list of comments of an input string that represent C-based single
    and multi-lined doc comments.
    """

    @dataclass
    class TemporaryComment:
        line: int
        column: int
        index: int
    
    class State(Enum):
        NORMAL = 0
        STRING = 1
        SINGLE_LINE = 2
        MULTI_LINE = 3

    result: list[DoccommentBlock] = []

    if len(text_file) < 2:
        return result
    
    stream = CharStream(text_file)

    state = State.NORMAL

    line = 1
    column = 0

    current = TemporaryComment(1, 1, 0)

    def current_start() -> int:
        return current.index

    def start_current(index: int):
        current.line = line
        current.column = column
        current.index = index

    def close_current(end_index: int):
        contents = stream.buffer[current_start():end_index]

        for pattern in doccomment_patterns:
            if contents.startswith(pattern):
                contents = contents[len(pattern):]
                
                final = DoccommentBlock(
                    file=path,
                    line=current.line,
                    column=current.column + len(pattern),
                    comment_contents=contents,
                    line_count=contents.count("\n") + 1
                )

                result.append(final)

                break
    
    while not stream.is_eof():
        char = stream.next()

        if char == "\n":
            column = 0
            line += 1
        else:
            column += 1

        match state:
            case State.NORMAL:
                if char == "\"":
                    state = State.STRING
                    continue
                
                if char != "/":
                    continue
                
                if stream.is_eof():
                    continue

                next = stream.peek()

                if next == "/":
                    state = State.SINGLE_LINE
                    start_current(stream.index - 1)
                elif next == "*":
                    state = State.MULTI_LINE
                    start_current(stream.index - 1)
            
            case State.STRING:
                if char == "\"":
                    state = State.NORMAL
            
            case State.SINGLE_LINE:
                # End of single line
                if char == "\n":
                    close_current(stream.index - 1)
                    state = State.NORMAL
            
            case State.MULTI_LINE:
                # End of multi-line
                if char == "*" and not stream.is_eof() and stream.peek() == "/":
                    close_current(stream.index - 1)
                    state = State.NORMAL
    
    # Finish any existing comment
    if state == State.SINGLE_LINE:
        close_current(stream.index - 1)
    elif state == State.MULTI_LINE:
        close_current(stream.index - 1)

    return result
