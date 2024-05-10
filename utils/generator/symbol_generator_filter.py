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
    enumFilters: list["DeclarationFilter"] = []
    enumMemberFilters: list["DeclarationFilter"] = []
    structFilters: list["DeclarationFilter"] = []
    methodFilters: list["DeclarationFilter"] = []

    @classmethod
    def from_config(cls, config: GeneratorConfig.Declarations.Filters):
        instance = cls()
        instance.enumFilters.extend(map(
            SymbolGeneratorFilter.RegexDeclarationFilter.from_string,
            config.enums
        ))
        instance.enumMemberFilters.extend(map(
            SymbolGeneratorFilter.RegexDeclarationFilter.from_string,
            config.enumMembers
        ))
        instance.structFilters.extend(map(
            SymbolGeneratorFilter.RegexDeclarationFilter.from_string,
            config.structs
        ))
        instance.methodFilters.extend(map(
            SymbolGeneratorFilter.RegexDeclarationFilter.from_string,
            config.methods
        ))
            
        return instance

    def should_gen_enum_extension(
        self, node: c_ast.Enum, decl: SwiftExtensionDecl
    ) -> bool:
        if decl.is_empty():
            return False
        
        return self.apply_filters(self.enumFilters, node, decl)

    def should_gen_enum_member(
        self, node: c_ast.Enumerator, decl: SwiftMemberDecl
    ) -> bool:
        
        return self.apply_filters(self.enumMemberFilters, node, decl)

    def should_gen_enum_var_member(
        self, node: c_ast.Enumerator, decl: SwiftMemberVarDecl
    ) -> bool:
        return self.should_gen_enum_member(node, decl)

    def should_gen_struct_extension(
        self, node: c_ast.Struct, decl: SwiftExtensionDecl
    ) -> bool:
        if decl.is_empty():
            return False
        
        return self.apply_filters(self.structFilters, node, decl)
    
    def should_gen_funcDecl(
        self, node: c_ast.FuncDecl, decl: SwiftDecl
    ) -> bool:
        
        return self.apply_filters(self.methodFilters, node, decl)
    
    def apply_filters(self, filters: Iterable["DeclarationFilter"], node: c_ast.Node, decl: SwiftDecl):
        result = SymbolGeneratorFilter.DeclarationFilterResult.NEITHER
        for filter in filters:
            result = result.combine(
                filter.filter_decl(node, decl)
            )
        
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
                case (cls.REJECT, _), (_, cls.REJECT):
                    return cls.REJECT
                case (cls.ACCEPT, _), (_, cls.ACCEPT):
                    return cls.ACCEPT
                case (cls.NEITHER, cls.NEITHER):
                    return cls.NEITHER

    class DeclarationFilter:
        "Base class for filters."
        neutralResult: "SymbolGeneratorFilter.DeclarationFilterResult"
        "Result of filter in case a positive match is not found. Defaults to `NEITHER`."

        def __init__(self):
            self.neutralResult = SymbolGeneratorFilter.DeclarationFilterResult.NEITHER

        def filter_decl(self, node: c_ast.Node, decl: SwiftDecl) -> "SymbolGeneratorFilter.DeclarationFilterResult":
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
            neutralResult = SymbolGeneratorFilter.DeclarationFilterResult.NEITHER

            if string.startswith("!"):
                pattern = pattern[1:]
                neutralResult = SymbolGeneratorFilter.DeclarationFilterResult.REJECT
            
            filter = cls(re.compile(pattern))
            filter.neutralResult = neutralResult
            return filter
        
        def filter_decl(self, node: c_ast.Node, decl: SwiftDecl):
            if decl.original_name is None:
                return self.neutralResult
            
            if self.pattern.match(decl.original_name.to_string()) is not None:
                return SymbolGeneratorFilter.DeclarationFilterResult.ACCEPT
            
            return self.neutralResult
