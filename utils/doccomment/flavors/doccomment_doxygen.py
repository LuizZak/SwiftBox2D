if __name__ == "__main__":
    import sys
    import pathlib

    sys.path.insert(0, str(pathlib.Path(__file__).joinpath("../../../../").resolve()))

import re
from typing import Any, Callable
from utils.data.c_decl_kind import CDeclKind
from utils.doccomment.flavors.string_manipulator import StringManipulator
from utils.doccomment.flavors.doccomment_flavor import DoccommentFlavor
from utils.data.swift_decl_lookup import SwiftDeclLookup
from utils.data.swift_decls import SwiftDecl
from utils.doccomment.doccomment_block import DoccommentBlock


class DoccommentFlavorDoxygen(DoccommentFlavor):
    def __init__(self):
        self.ref_regex = re.compile(r"\\ref (\w+(?:\(\))?)", re.IGNORECASE)
        self.backtick_regex = re.compile(r"`([^`]+)`")
        self.backtick_word_regex = re.compile(r"\w+")
        self.backtick_cpp_member_regex = re.compile(r"(\w+)::(\w+)")

    def doccomment_patterns(self) -> list[str]:
        return [
            "//!<",
            "//!",
            "///",
            "/**",
        ]

    def transform_doccomment(
        self, comment: DoccommentBlock | None, decl: SwiftDecl, lookup: SwiftDeclLookup
    ) -> DoccommentBlock | None:
        if comment is None:
            return None

        # Replace "\ref <symbol[::symbol...]>" with "`<symbol[.symbol...]>`"
        comment = self.handle_command(
            comment,
            r"ref\s",
            lambda range: range.replace(
                self.__convert_ref(range.extend(r"\w+(::\w+)*(\(\))?"), lookup)
            ),
        )
        # Remove \brief markers
        comment = self.handle_command(
            comment, "brief", lambda range: (range.extend_whitespace(), range.remove())
        )
        # Remove '\ingroup*' lines
        comment = self.handle_command(
            comment,
            "ingroup",
            lambda range: (range.extend_to_newline(), range.remove()),
        )
        # Replace '@param <symbol>' with '- param <symbol>:'
        comment = self.handle_command(
            comment,
            "param",
            lambda range: (
                range.extend_whitespace(),
                range.replace(f"- param {range.extend(r"\w+")}:"),
            ),
        )
        # Reword '@return' with '- returns:'
        comment = self.handle_command(
            comment, "return", lambda range: range.replace("- returns:")
        )
        # Reword '\note' to '- note:'
        comment = self.handle_command(
            comment, "note", lambda range: range.replace("- note:")
        )

        return comment

    @staticmethod
    def handle_command(
        comment: DoccommentBlock,
        name: str,
        handler: Callable[["StringManipulator"], Any],
    ) -> DoccommentBlock:
        pattern = re.compile(rf"[@\\]{name}")

        buffer = comment.comment_contents
        start_index = 0

        while match := pattern.search(buffer, start_index):
            start_index = match.start(0) + 1

            manipulator = StringManipulator(buffer, match.start(0))
            manipulator.extend_to(match.end(0))
            handler(manipulator)

            new_buffer = manipulator.get_buffer()
            if buffer == new_buffer:
                break

            buffer = new_buffer

        return comment.with_contents(buffer)

    @staticmethod
    def __convert_ref(
        symbol_name: str | None,
        lookup: SwiftDeclLookup,
    ) -> str | None:
        def __convert_ref_internal(
            inner_symbol_name: str | None
        ) -> str | None:
            if inner_symbol_name is None:
                return None

            # C++ namespaced symbol references
            if "::" in inner_symbol_name:
                split = inner_symbol_name.split("::")
                replaced = map(lambda s: __convert_ref_internal(s), split)
                return ".".join([r for r in replaced if r is not None])

            swift_name = lookup.lookup_c_symbol(inner_symbol_name)
            return swift_name if swift_name is not None else inner_symbol_name

        return f"`{__convert_ref_internal(symbol_name)}`"


if __name__ == "__main__":
    from pathlib import Path
    from utils.data.compound_symbol_name import CompoundSymbolName
    from utils.data.swift_decls import SwiftMemberVarDecl

    dummy_decl = SwiftMemberVarDecl(
        name=CompoundSymbolName.from_pascal_case("SwiftSymbol"),
        original_name="c_symbol",
        origin=None,
        original_node=None,
        c_kind=CDeclKind.STRUCT,
        doccomment=None,
    )
    lookup = SwiftDeclLookup.from_decls([dummy_decl])

    test_comment = DoccommentBlock(
        Path("dummy"),
        1,
        1,
        "\\ingroup Groupname\n\\brief \\ref c_symbol::abc is a symbol.\n\\note This is a note!\n@param p A parameter\n@return A return value.",
        line_count=0,
    )

    formatter = DoccommentFlavorDoxygen()
    result = formatter.transform_doccomment(test_comment, dummy_decl, lookup)

    assert result is not None
    print(result.comment_contents)
