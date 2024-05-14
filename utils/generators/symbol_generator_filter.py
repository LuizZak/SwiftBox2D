import re
from enum import Enum
from typing import Iterable
from pycparser import c_ast

from utils.data.generator_config import GeneratorConfig
from utils.data.swift_decls import (
    SwiftDecl,
    SwiftExtensionDecl,
    SwiftMemberDecl,
    SwiftMemberVarDecl,
)


class SymbolGeneratorFilter:
    """
    Class responsible for selecting which C symbols get converted into Swift symbol
    declarations.
    """

    enum_filters: list["DeclarationFilter"] = []
    enum_member_filters: list["DeclarationFilter"] = []
    struct_filters: list["DeclarationFilter"] = []
    method_filters: list["DeclarationFilter"] = []
    implicit: list[str] = []
    "List of implicit typename filters that indicate a typename should be allowed, if no denying filters match the typename."

    @classmethod
    def from_config(cls, config: GeneratorConfig.Declarations):
        instance = cls()
        instance.enum_filters.extend(
            map(
                SymbolGeneratorFilter.RegexDeclarationFilter.from_string,
                config.filters.enums,
            )
        )
        instance.enum_member_filters.extend(
            map(
                SymbolGeneratorFilter.RegexDeclarationFilter.from_string,
                config.filters.enum_members,
            )
        )
        instance.struct_filters.extend(
            map(
                SymbolGeneratorFilter.RegexDeclarationFilter.from_string,
                config.filters.structs,
            )
        )
        instance.method_filters.extend(
            map(
                SymbolGeneratorFilter.RegexDeclarationFilter.from_string,
                config.filters.methods,
            )
        )
        instance.implicit.extend(map(lambda c: c.c_name, config.conformances))

        return instance

    def should_gen_enum_extension(
        self, node: c_ast.Enum, decl: SwiftExtensionDecl
    ) -> bool:
        if decl.is_empty():
            return False

        return self.apply_filters(self.enum_filters, node, decl)

    def should_gen_enum_member(
        self, node: c_ast.Enumerator, decl: SwiftMemberDecl
    ) -> bool:
        return self.apply_filters(self.enum_member_filters, node, decl)

    def should_gen_enum_var_member(
        self, node: c_ast.Enumerator, decl: SwiftMemberVarDecl
    ) -> bool:
        return self.should_gen_enum_member(node, decl)

    def should_gen_struct_extension(
        self, node: c_ast.Struct, decl: SwiftExtensionDecl
    ) -> bool:
        if decl.is_empty():
            return False

        return self.apply_filters(self.struct_filters, node, decl)

    def should_gen_func_decl(self, node: c_ast.FuncDecl, decl: SwiftDecl) -> bool:
        # An extension method generation?
        if isinstance(decl, SwiftExtensionDecl) and len(decl.members) > 0:
            return self.apply_filters(self.method_filters, node, decl.members[0])

        return self.apply_filters(self.method_filters, node, decl)

    def apply_filters(
        self, filters: Iterable["DeclarationFilter"], node: c_ast.Node, decl: SwiftDecl
    ):
        result = SymbolGeneratorFilter.DeclarationFilterResult.NEITHER

        # Verify implicit filters
        if decl.original_name is not None:
            original_name = decl.original_name
            if original_name in self.implicit:
                result = SymbolGeneratorFilter.DeclarationFilterResult.ACCEPT

        for filter in filters:
            result = result.combine(filter.filter_decl(node, decl))

        return result == SymbolGeneratorFilter.DeclarationFilterResult.ACCEPT

    class DeclarationFilterResult(Enum):
        """
        Specifiers the result of a filter, either as an accept, reject, or indifferent
        case. Declarations must have at least one `ACCEPT` filter result, with no
        `REJECT` results in order not be discarded.
        """

        NEITHER = 0
        """
        Filtering result that is negative, but does not reject a symbol in case
        a different filter on the same symbol returns `ACCEPT`.
        """

        ACCEPT = 1
        """
        Positive filter result. A symbol has to have at least one `ACCEPT` filter
        pass, with no `REJECT`s, in order to be generated.
        """

        REJECT = 2
        """
        Negative filter result. A symbol that has this value as a result of one
        of the filters is not generated, regardless of the presence of `ACCEPT`
        results.
        """

        def combine(self, other: "SymbolGeneratorFilter.DeclarationFilterResult"):
            cls = SymbolGeneratorFilter.DeclarationFilterResult
            match (self, other):
                case (cls.REJECT, _) | (_, cls.REJECT):
                    return cls.REJECT
                case (cls.ACCEPT, _) | (_, cls.ACCEPT):
                    return cls.ACCEPT
                case (cls.NEITHER, cls.NEITHER):
                    return cls.NEITHER

    class DeclarationFilter:
        "Base class for filters."

        neutral_result: "SymbolGeneratorFilter.DeclarationFilterResult"
        "Result of filter in case a positive match is not found. Defaults to `NEITHER`."
        positive_result: "SymbolGeneratorFilter.DeclarationFilterResult"
        "Result of filter in case a positive match is found. Defaults to `ACCEPT`."

        def __init__(self):
            self.neutral_result = SymbolGeneratorFilter.DeclarationFilterResult.NEITHER
            self.positive_result = SymbolGeneratorFilter.DeclarationFilterResult.ACCEPT

        def filter_decl(
            self, node: c_ast.Node, decl: SwiftDecl
        ) -> "SymbolGeneratorFilter.DeclarationFilterResult":
            return SymbolGeneratorFilter.DeclarationFilterResult.NEITHER

    class RegexDeclarationFilter(DeclarationFilter):
        "A declaration filter that filters based on the regex of the original C symbol name."

        pattern: re.Pattern

        def __init__(self, pattern: re.Pattern):
            super().__init__()
            self.pattern = pattern

        @classmethod
        def from_string(cls, string: str):
            pattern = string
            positive_result = SymbolGeneratorFilter.DeclarationFilterResult.ACCEPT

            if string.startswith("!"):
                pattern = pattern[1:]
                positive_result = SymbolGeneratorFilter.DeclarationFilterResult.REJECT

            filter = cls(re.compile(pattern))
            filter.positive_result = positive_result
            return filter

        def filter_decl(self, node: c_ast.Node, decl: SwiftDecl):
            if decl.original_name is None:
                return self.neutral_result

            if self.pattern.match(decl.original_name) is not None:
                return self.positive_result

            return self.neutral_result
