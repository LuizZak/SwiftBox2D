from utils.data.swift_decl_lookup import SwiftDeclLookup
from utils.data.swift_decls import SwiftDecl
from utils.doccomment.doccomment_block import DoccommentBlock


class DoccommentFlavor:
    """
    Describes a type of code documentation and provides hooks to transform syntaxes
    from a flavor into recognizable Swift doc comments.
    """

    def doccomment_patterns(self) -> list[str]:
        """Gets a list of C-style comment patterns that indicate a doc comment of this flavor's specification. Must be overridden by subclasses."""
        raise NotImplementedError()

    def transform_doccomment(
        self, comment: DoccommentBlock | None, decl: SwiftDecl, lookup: SwiftDeclLookup
    ) -> DoccommentBlock | None:
        """
        Transforms doc comments using this flavor's specification.
        Must be overridden by subclasses.
        A callee expects that no mutation occur in `decl` or `comment` during this
        method.
        """
        raise NotImplementedError()
