from dataclasses import dataclass
from pathlib import Path
from typing import Iterable

from pycparser import c_ast
from utils.converters.swift_type_mapper import SwiftTypeMapper
from utils.cutils.cutils import declaration_from_type
from utils.data.c_decl_kind import CDeclKind
from utils.data.compound_symbol_name import CompoundSymbolName
from utils.data.generator_config import GeneratorConfig
from utils.data.swift_decl_lookup import SwiftDeclLookup
from utils.data.swift_decls import (
    SourceLocation,
    SwiftAccessLevel,
    SwiftDecl,
    SwiftExtensionDecl,
    SwiftMemberFunctionDecl,
    SwiftMemberVarDecl,
    SwiftTypealiasDecl,
)
from utils.data.swift_type import SwiftType
from utils.generators.known_conformance_generators import get_conformance_generator
from utils.generators.symbol_generator_filter import SymbolGeneratorFilter
from utils.generators.symbol_name_generator import SymbolNameGenerator


# Visitor / declaration collection
def coord_to_location(coord) -> SourceLocation:
    return SourceLocation(Path(coord.file), coord.line, coord.column)


class SwiftDeclGenerator:
    @dataclass(slots=True)
    class DeclGenerateContext:
        ast: c_ast.FileAST
        type_mapper: SwiftTypeMapper

    class MemberMethodGenerator:
        method_prefix: str
        class_to_map: CompoundSymbolName
        first_argument_member: str
        first_argument_type: str
        access_level: SwiftAccessLevel

        def __init__(
            self,
            method_prefix: str,
            class_to_map: CompoundSymbolName | str,
            first_argument_member: str,
            first_argument_type: str,
            access_level: SwiftAccessLevel,
        ):
            self.method_prefix = method_prefix
            if isinstance(class_to_map, CompoundSymbolName):
                self.class_to_map = class_to_map
            else:
                self.class_to_map = CompoundSymbolName.from_pascal_case(class_to_map)
            self.first_argument_member = first_argument_member
            self.first_argument_type = first_argument_type
            self.access_level = access_level

        @classmethod
        def from_config(
            cls, config: GeneratorConfig.Declarations.FunctionToMethodMapper
        ):
            return cls(
                method_prefix=config.c_prefix,
                class_to_map=config.swift_type,
                first_argument_member=config.param0[0],
                first_argument_type=config.param0[1],
                access_level=SwiftAccessLevel(config.access_level),
            )

        def transform(
            self,
            node: c_ast.FuncDecl,
            func_name: CompoundSymbolName,
            context: "SwiftDeclGenerator.DeclGenerateContext",
        ) -> SwiftMemberFunctionDecl | None:
            if len(node.args.params) < 1:
                return None

            def map_argument(p) -> tuple[SwiftMemberFunctionDecl.ParameterType, str]:
                decl = declaration_from_type(p.type)
                type = context.type_mapper.map_to_swift_type(p.type, context.ast)
                type_decorator: str | None = None
                invocation = decl[0] if decl is not None else "?"

                # Ensure function pointer arguments are converted into appropriate
                # `@convention(c)` closure parameters
                if type is not None:
                    if typename := type.as_typename_type():
                        if unaliased := context.type_mapper.unalias_type(
                            typename.name, context.ast
                        ):
                            if f_type := unaliased.as_function_type():
                                type = f_type
                                type_decorator = "@convention(c)"

                return (
                    SwiftMemberFunctionDecl.ParameterType(
                        None,
                        decl[0] if decl is not None else "?",
                        type_decorator,
                        type if type is not None else SwiftType.type_name("?"),
                    ),
                    invocation,
                )

            # Generate arguments for function
            arguments = [map_argument(a) for a in node.args.params[1:]]

            c_call_args = [self.first_argument_member] + [a[1] for a in arguments]
            return_type = context.type_mapper.map_to_swift_type(
                node.type.type, context.ast
            )

            return SwiftMemberFunctionDecl(
                c_kind=CDeclKind.FUNC,
                name=func_name,
                original_name=node.type.declname,
                parameters=[a[0] for a in arguments],
                return_type=return_type,
                origin=coord_to_location(node.coord),
                original_node=node,
                doccomment=None,
                body=[
                    # Default body just calls the C decl using a configured first argument and the rest of the arguments from the original function
                    f"{node.type.declname}({", ".join(c_call_args)})"
                ],
                access_level=self.access_level,
            )

    @dataclass
    class ConformanceRequest:
        symbol_name: str
        conformances: list[str]
        satisfied: bool = False

        @classmethod
        def from_config(cls, config: GeneratorConfig.Declarations.ConformanceEntry):
            return cls(symbol_name=config.c_name, conformances=config.conformances)

    def __init__(
        self,
        prefixes: Iterable[str],
        symbol_filter: SymbolGeneratorFilter,
        symbol_name_generator: SymbolNameGenerator,
        conformances: Iterable[ConformanceRequest],
        method_mappers: Iterable[MemberMethodGenerator],
    ):
        self.prefixes = list(prefixes)
        self.symbol_filter = symbol_filter
        self.symbol_name_generator = symbol_name_generator
        self.conformances = list(conformances)
        self.method_mappers = list(method_mappers)

    @classmethod
    def from_config(cls, config: GeneratorConfig.Declarations):
        return cls(
            prefixes=config.prefixes,
            symbol_filter=SymbolGeneratorFilter.from_config(config),
            symbol_name_generator=SymbolNameGenerator.from_config(config),
            conformances=map(cls.ConformanceRequest.from_config, config.conformances),
            method_mappers=map(
                cls.MemberMethodGenerator.from_config, config.functions_to_methods
            ),
        )

    # Enum

    def generate_enum_case(
        self,
        enum_name: CompoundSymbolName,
        enum_original_name: str,
        node: c_ast.Enumerator,
        context: DeclGenerateContext,
    ) -> SwiftMemberVarDecl | None:
        return SwiftMemberVarDecl(
            self.symbol_name_generator.generate_enum_case(
                enum_name, enum_original_name, node.name
            ),
            node.name,
            coord_to_location(node.coord),
            original_node=node,
            c_kind=CDeclKind.ENUM_CASE,
            doccomment=None,
            is_static=True,
            initial_value=node.name,
        )

    def generate_enum(
        self,
        node: c_ast.Enum,
        context: DeclGenerateContext,
    ) -> SwiftExtensionDecl | None:
        decl_name = node.name
        enum_name = self.symbol_name_generator.generate_enum_name(decl_name)

        conformances = self._propose_conformances(decl_name)

        members = []
        if node.values is not None:
            for case_node in node.values:
                case_decl = self.generate_enum_case(
                    enum_name, decl_name, case_node, context
                )
                if case_decl is None:
                    continue

                if self.symbol_filter.should_gen_enum_var_member(case_node, decl_name):
                    members.append(case_decl)

        decl = SwiftExtensionDecl(
            enum_name,
            decl_name,
            coord_to_location(node.coord),
            original_node=node,
            c_kind=CDeclKind.ENUM,
            doccomment=None,
            members=list(members),
            conformances=conformances,
            access_level=SwiftAccessLevel.PUBLIC,
        )

        if decl.is_empty():
            return None

        return decl

    # Struct

    def generate_struct(
        self,
        node: c_ast.Struct,
        context: DeclGenerateContext,
    ) -> SwiftExtensionDecl | None:
        decl_name = node.name

        conformances = self._propose_conformances(decl_name)

        struct_name = self.symbol_name_generator.generate_struct_name(decl_name)

        decl = SwiftExtensionDecl(
            struct_name,
            decl_name,
            coord_to_location(node.coord),
            original_node=node,
            c_kind=CDeclKind.STRUCT,
            doccomment=None,
            members=[],
            conformances=conformances,
            access_level=SwiftAccessLevel.PUBLIC,
        )

        if decl.is_empty():
            return None

        return decl

    # Function

    def generate_func_decl(
        self,
        node: c_ast.FuncDecl,
        context: DeclGenerateContext,
    ) -> SwiftDecl | None:
        if node.args is None:
            return None

        c_func_name: str = node.type.declname
        transformer = self._propose_method_generator(c_func_name, node.args)

        if transformer is None:
            return None
        if not isinstance(node.type, c_ast.TypeDecl):
            return None

        interim_name = c_func_name[len(transformer.method_prefix) :]
        if len(interim_name) == 0:
            return None

        func_name = self.symbol_name_generator.generate_func_decl_name(interim_name)

        method = transformer.transform(node, func_name, context)
        if method is None:
            return None
        access_level = (
            method.access_level
            if method.access_level is not None
            else SwiftAccessLevel.PUBLIC
        )

        # Reset method's access level as it will be redundant if exported alongside
        # extension's access level
        method.access_level = None

        return SwiftExtensionDecl(
            name=transformer.class_to_map,
            original_name=None,
            origin=None,
            original_node=None,
            c_kind=CDeclKind.FUNC,
            doccomment=None,
            members=[method],
            conformances=[],
            access_level=access_level,
        )

    def _propose_method_generator(
        self,
        c_name: str,
        args: c_ast.ParamList,
    ) -> MemberMethodGenerator | None:
        if len(args.params) < 1:
            return None

        for map in self.method_mappers:
            if c_name.startswith(map.method_prefix):
                return map

        return None

    def _propose_conformances(self, c_decl_name: str) -> list[str]:
        result = []

        # Match required protocols
        for req in self.conformances:
            if req.symbol_name != c_decl_name:
                continue

            req.satisfied = True

            result.extend(req.conformances)

        return list(set(result))

    def _name_from_decl(self, c_decl: c_ast.Node) -> str | None:
        if isinstance(c_decl, c_ast.FuncDecl):
            return c_decl.type.declname
        if isinstance(c_decl, c_ast.Typedef):
            return c_decl.name
        if isinstance(c_decl, c_ast.Struct):
            return c_decl.name
        if isinstance(c_decl, c_ast.Enum):
            return c_decl.name

        return None

    #

    def generate(
        self,
        node: c_ast.Node,
        context: DeclGenerateContext,
    ) -> SwiftDecl | None:
        decl_name = self._name_from_decl(node)

        match node:
            case c_ast.Enum():
                if not self.symbol_filter.should_gen_enum_extension(node, decl_name):
                    return None

                if (decl := self.generate_enum(node, context)) is not None:
                    return decl

            case c_ast.Struct():
                if not self.symbol_filter.should_gen_struct_extension(node, decl_name):
                    return None

                if (decl := self.generate_struct(node, context)) is not None:
                    return decl

            case c_ast.FuncDecl():
                if not self.symbol_filter.should_gen_func_decl(node, decl_name):
                    return None

                if (f_decl := self.generate_func_decl(node, context)) is not None:
                    return f_decl

        return None

    # MARK: Entry point

    def generate_from_list(
        self,
        nodes: list[c_ast.Node],
        ast: c_ast.FileAST,
    ) -> list[SwiftDecl]:
        result = []

        type_mapper = SwiftTypeMapper()
        type_mapper.enable_caching(ast)
        context = self.DeclGenerateContext(ast=ast, type_mapper=type_mapper)

        for node in nodes:
            decl = self.generate(node, context)
            if decl is not None:
                result.append(decl)

        return result

    def post_merge(self, decls: list[SwiftDecl]) -> list[SwiftDecl]:
        """Applies post-type merge operations to a list of Swift declarations"""
        decls = list(decls)  # Copy internally first

        def _generate_typealiases(decls: list[SwiftDecl]):
            # Generate typealiases for C symbols, if necessary
            typealiases: list[SwiftDecl] = []

            for decl in decls:
                if not isinstance(decl, SwiftExtensionDecl) or not (
                    isinstance(decl.original_node, c_ast.Struct)
                    or isinstance(decl.original_node, c_ast.Enum)
                ):
                    continue

                if (
                    decl.original_name is not None
                    and decl.name.to_string() != decl.original_name
                ):
                    type_alias = SwiftTypealiasDecl(
                        name=decl.name,
                        original_name=decl.original_name,
                        original_node=decl.original_node,
                        origin=decl.origin,
                        c_kind=decl.c_kind,
                        access_level=decl.access_level,
                        doccomment=decl.doccomment,
                    )
                    decl.doccomment = None  # Erase doc comment from original declaration in favor of the typealias
                    typealiases.append(type_alias)

            return typealiases

        decls = _generate_typealiases(decls) + decls

        # Use proposed conformances to generate required members
        for decl in decls:
            if not isinstance(decl, SwiftExtensionDecl):
                continue
            if not isinstance(decl.original_node, c_ast.Struct):
                continue

            for conformance in sorted(decl.conformances):
                if gen := get_conformance_generator(conformance):
                    decl.members.extend(gen.generate_members(decl, decl.original_node))

        # Convert types in method/properties signatures to Swift aliased types,
        # if possible
        lookup = SwiftDeclLookup.from_decls(decls)
        for decl in decls:
            if not isinstance(decl, SwiftExtensionDecl):
                continue

            for member in decl.members:
                if isinstance(member, SwiftMemberFunctionDecl):
                    if ret_type := member.return_type:
                        if ret_type_name := ret_type.as_typename_type():
                            if resolved := lookup.lookup_c_symbol(ret_type_name.name):
                                member.return_type = SwiftType.type_name(resolved)

                    for i in range(len(member.parameters)):
                        arg = member.parameters[i]
                        if (type_name := arg.type.as_typename_type()) is None:
                            continue

                        if (resolved := lookup.lookup_c_symbol(type_name.name)) is None:
                            continue

                        member.parameters[i].type = SwiftType.type_name(resolved)

        return decls
