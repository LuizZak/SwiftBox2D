from typing import Sequence
from utils.collection.collection_utils import flatten
from utils.data.generator_config import GeneratorConfig
from utils.data.swift_decl_lookup import SwiftDeclLookup
from utils.data.swift_decl_visitor import SwiftDeclCallableVisitor
from utils.data.swift_decls import SwiftDecl, SwiftDeclWalker
from utils.doccomment.doccomment_formatter import DoccommentFormatter
from utils.doccomment.doccomment_lookup import DoccommentLookup
from utils.doccomment.flavors.doccomment_doxygen import DoccommentFlavorDoxygen
from utils.doccomment.flavors.doccomment_flavor import DoccommentFlavor


class DoccommentManager:
    def __init__(
        self,
        lookup: DoccommentLookup,
        flavors: list[DoccommentFlavor],
        formatter: DoccommentFormatter,
        should_collect: bool,
        should_format: bool,
    ):
        self.lookup = lookup
        self.flavors = flavors
        self.formatter = formatter
        self.should_collect = should_collect
        self.should_format = should_format

    @classmethod
    def from_config(cls, config: GeneratorConfig.DocComments):
        flavors: list[DoccommentFlavor] = [DoccommentFlavorDoxygen()]

        return cls(
            lookup=DoccommentLookup(
                doccomment_patterns=flatten(
                    pat for pat in (flavor.doccomment_patterns() for flavor in flavors)
                )
            ),
            flavors=flavors,
            formatter=DoccommentFormatter(),
            should_collect=config.collect,
            should_format=config.format,
        )

    def populate(self, decls: Sequence[SwiftDecl]):
        """Populates doc comments for provided declarations. Comments are sourced from each declaration's `origin`."""

        if not self.should_collect:
            return

        self.lookup.populate_doc_comments_inplace(decls)

    def format(self, decls: Sequence[SwiftDecl]):
        """Formats doc comments from provided declarations inplace."""

        if not self.should_format:
            return

        swift_lookup = SwiftDeclLookup.from_decls(decls)
        visitor = SwiftDeclCallableVisitor(
            lambda decl: self.__format(decl, swift_lookup)
        )
        walker = SwiftDeclWalker(visitor)

        for decl in decls:
            walker.walk_decl(decl)

    def __format(self, decl: SwiftDecl, swift_lookup: SwiftDeclLookup):
        for flavor in self.flavors:
            decl.doccomment = flavor.transform_doccomment(
                decl.doccomment, decl, swift_lookup
            )

        decl.doccomment = self.formatter.format_doccomment(
            decl.doccomment, decl, swift_lookup
        )
