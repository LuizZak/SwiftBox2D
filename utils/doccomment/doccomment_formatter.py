from typing import Callable, Sequence, TypeVar
from utils.data.generator_config import GeneratorConfig
from utils.data.swift_decl_lookup import SwiftDeclLookup
from utils.data.swift_decls import SwiftDecl
from utils.doccomment.doccomment_block import DoccommentBlock


class DoccommentFormatter:
    T = TypeVar("T")
    DOC_T = TypeVar("DOC_T", DoccommentBlock, str)

    @classmethod
    def from_config(cls, config: GeneratorConfig.DocComments):
        return cls()

    def format_doccomment(
        self,
        comment: DoccommentBlock | None,
        decl: SwiftDecl,
        decl_lookup: SwiftDeclLookup,
    ) -> DoccommentBlock | None:
        """
        Requests that a given doccomment block be formatted and returned as a copy.
        A callee expects that no mutation occur in `decl` or `comment` during this
        method.
        """

        if comment is None:
            return None

        # Format multi-line comments
        if comment.is_multi_lined():
            comment = self.format_multiline(comment)
        else:
            comment = self.format_singleline(comment)

        return comment

    def format_multiline(self, comment: DoccommentBlock) -> DoccommentBlock:
        """
        Requests that a given doccomment block be formatted as a multi-lined comment
        and returned as a copy.
        A callee expects that no mutation occur in `comment` during this method.
        """

        # Use shallowest indentation for re-indenting
        comment = comment.normalize_indentation()

        # Trim leading and trailing empty lines
        lines = self._trim_empty_lines(
            comment.lines(), lambda line: len(line.strip()) == 0
        )

        return comment.with_lines(lines)

    def format_singleline(self, comment: DoccommentBlock) -> DoccommentBlock:
        """
        Requests that a given doccomment block be formatted as a single line comment
        and returned as a copy.
        A callee expects that no mutation occur in `comment` during this method.
        """

        # Trim leading spaces
        return comment.with_contents(comment.comment_contents.lstrip())

    def _trim_empty_lines(
        self, sequence: Sequence[T], is_empty: Callable[[T], bool]
    ) -> list[T]:
        """
        Trims empty entries of a sequence based on predicate `is_empty`. Returns
        the outermost range of items where `is_empty(<item>)` is False.
        If all items are empty according to `is_empty`, the original sequence is
        returned unchanged.
        """

        has_content = False
        first_index: int | None = None
        last_index: int | None = None

        for i, comment in enumerate(sequence):
            if not is_empty(comment):
                has_content = True

                if first_index is None:
                    first_index = i
                if last_index is None or last_index < i:
                    last_index = i

        if not has_content:
            return list(sequence)

        if (first_index is not None) and (last_index is not None):
            return list(sequence[first_index : (last_index + 1)])

        return list(sequence)
