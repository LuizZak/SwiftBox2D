from dataclasses import dataclass
from pathlib import Path
from typing import Iterable

from pycparser import c_ast
from utils.converters.swift_type_mapper import SwiftTypeMapper
from utils.cutils.cutils import declarationFromType
from utils.data.compound_symbol_name import CompoundSymbolName
from utils.data.generator_config import GeneratorConfig
from utils.data.swift_decls import (
    CDeclKind,
    SourceLocation,
    SwiftAccessLevel,
    SwiftDecl,
    SwiftExtensionDecl,
    SwiftMemberFunctionDecl,
    SwiftMemberVarDecl,
)
from utils.generator.known_conformance_generators import get_conformance_generator
from utils.generator.symbol_generator_filter import SymbolGeneratorFilter
from utils.generator.symbol_name_generator import SymbolNameGenerator


# Visitor / declaration collection
def coord_to_location(coord) -> SourceLocation:
    return SourceLocation(Path(coord.file), coord.line, coord.column)


class SwiftDeclGenerator:
    class MemberMethodGenerator:
        methodPrefix: str
        classToMap: CompoundSymbolName
        firstArgumentMember: str
        firstArgumentType: str
        accessLevel: SwiftAccessLevel

        def __init__(
            self,
            methodPrefix: str,
            classToMap: CompoundSymbolName | str,
            firstArgumentMember: str,
            firstArgumentType: str,
            accessLevel: SwiftAccessLevel
        ):
            self.methodPrefix = methodPrefix
            if isinstance(classToMap, CompoundSymbolName):
                self.classToMap = classToMap
            else:
                self.classToMap = CompoundSymbolName.from_pascal_case(classToMap)
            self.firstArgumentMember = firstArgumentMember
            self.firstArgumentType = firstArgumentType
            self.accessLevel = accessLevel
        
        @classmethod
        def from_config(cls, config: GeneratorConfig.Declarations.FunctionToMethodMapper):
            return cls(
                methodPrefix=config.cPrefix,
                classToMap=config.swiftType,
                firstArgumentMember=config.param0[0],
                firstArgumentType=config.param0[1],
                accessLevel=SwiftAccessLevel(config.accessLevel)
            )

        def transform(
            self,
            typeMapper: SwiftTypeMapper,
            node: c_ast.FuncDecl,
            fName: CompoundSymbolName,
            context: c_ast.FileAST
        ) -> SwiftMemberFunctionDecl | None:

            if len(node.args.params) < 1:
                return None
            
            def mapArgument(p) -> tuple[SwiftMemberFunctionDecl.ARG_TYPE, str]:
                decl = declarationFromType(p.type)
                type = typeMapper.map_to_swift_type(p.type, context)
                type_str = type.to_string() if type is not None else "?"
                invocation = decl[0] if decl is not None else "?"

                # Ensure function pointer arguments are converted into appropriate
                # `@convention(c)` closure parameters
                if type is not None:
                    if typename := type.as_typename_type():
                        if unaliased := typeMapper.unalias_type(typename.name, context):
                            if fType := unaliased.as_function_type():
                                # args = ", ".join(f"${i}" for i in range(len(fType.parameters)))
                                type_str = f"@convention(c) {fType.to_string()}"
                                # invocation = f"{{ {invocation}({args}) }}"

                return ((
                    None,
                    decl[0] if decl is not None else "?",
                    type_str
                ), invocation)
            
            # Generate arguments for function
            arguments = [mapArgument(a) for a in node.args.params[1:]]

            cCallArgs = [self.firstArgumentMember] + [a[1] for a in arguments]
            returnType = typeMapper.map_to_swift_type(node.type.type, context)

            return SwiftMemberFunctionDecl(
                c_kind=CDeclKind.FUNC,
                name=fName,
                original_name=node.type.declname,
                arguments=[a[0] for a in arguments],
                return_type=returnType.to_string() if returnType is not None else None,
                origin=coord_to_location(node.coord),
                original_node=node,
                doccomment=None,
                body=[
                    # Default body just calls the C decl using a configured first argument and the rest of the arguments from the original function
                    f"{node.type.declname}({', '.join(cCallArgs)})"
                ],
                access_level=self.accessLevel
            )

    @dataclass
    class ConformanceRequest:
        symbolName: str
        conformances: list[str]
        satisfied: bool = False

        @classmethod
        def from_config(cls, config: GeneratorConfig.Declarations.ConformanceEntry):
            return cls(
                symbolName=config.cName,
                conformances=config.conformances
            )

    def __init__(
        self,
        prefixes: Iterable[str],
        symbol_filter: SymbolGeneratorFilter,
        symbol_name_generator: SymbolNameGenerator,
        conformances: Iterable[ConformanceRequest],
        methodMappers: Iterable[MemberMethodGenerator]
    ):
        self.prefixes = list(prefixes)
        self.symbol_filter = symbol_filter
        self.symbol_name_generator = symbol_name_generator
        self.conformances = list(conformances)
        self.methodMappers = list(methodMappers)
        self.typeMapper = SwiftTypeMapper()

    @classmethod
    def from_config(cls, config: GeneratorConfig.Declarations):
        return cls(
            prefixes=config.prefixes,
            symbol_filter=SymbolGeneratorFilter.from_config(config),
            symbol_name_generator=SymbolNameGenerator.from_config(config),
            conformances=map(cls.ConformanceRequest.from_config, config.conformances),
            methodMappers=map(cls.MemberMethodGenerator.from_config, config.functionsToMethods)
        )

    # Enum

    def generate_enum_case(
        self,
        enum_name: CompoundSymbolName,
        enum_original_name: str,
        node: c_ast.Enumerator,
        context: c_ast.FileAST
    ) -> SwiftMemberVarDecl | None:

        value = self.symbol_name_generator.generate_original_enum_case(node.name).to_string()

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
            initial_value=value
        )

    def generate_enum(self, node: c_ast.Enum, context: c_ast.FileAST) -> SwiftExtensionDecl | None:
        enum_name = self.symbol_name_generator.generate_enum_name(node.name)

        members = []
        if node.values is not None:
            for case_node in node.values:
                case_decl = self.generate_enum_case(enum_name, node.name, case_node, context)
                if case_decl is None:
                    continue

                if self.symbol_filter.should_gen_enum_var_member(case_node, case_decl):
                    members.append(case_decl)

        decl = SwiftExtensionDecl(
            enum_name,
            node.name,
            coord_to_location(node.coord),
            original_node=node,
            c_kind=CDeclKind.ENUM,
            doccomment=None,
            members=list(members),
            conformances=[],
            access_level=SwiftAccessLevel.PUBLIC
        )

        if conformances := self.propose_conformances(decl):
            decl.conformances.extend(conformances)
        
        return decl

    # Struct

    def generate_struct(self, node: c_ast.Struct, context: c_ast.FileAST) -> SwiftExtensionDecl | None:
        struct_name = self.symbol_name_generator.generate_struct_name(node.name)

        decl = SwiftExtensionDecl(
            struct_name,
            node.name,
            coord_to_location(node.coord),
            original_node=node,
            c_kind=CDeclKind.STRUCT,
            doccomment=None,
            members=[],
            conformances=[],
            access_level=SwiftAccessLevel.PUBLIC
        )

        if conformances := self.propose_conformances(decl):
            decl.conformances.extend(conformances)

        return decl
    
    # Function

    def generate_funcDecl(self, node: c_ast.FuncDecl, context: c_ast.FileAST) -> SwiftDecl | None:
        if node.args is None:
            return None
        
        funcName: str = node.type.declname
        transformer = self._proposeMethodGenerator(funcName, node.args)

        if transformer is None:
            return None
        if not isinstance(node.type, c_ast.TypeDecl):
            return None
        
        interimName = funcName[len(transformer.methodPrefix):]
        if len(interimName) == 0:
            return None

        fName = self.symbol_name_generator.generate_funcDecl_name(interimName)

        method = transformer.transform(self.typeMapper, node, fName, context)
        if method is None:
            return None
        access_level = method.access_level if method.access_level is not None else SwiftAccessLevel.PUBLIC

        # Reset method's access level as it will be redundant if exported alongside
        # extension's access level
        method.access_level = None

        return SwiftExtensionDecl(
            name=transformer.classToMap,
            original_name=None,
            origin=coord_to_location(node.coord),
            original_node=node,
            c_kind=CDeclKind.FUNC,
            doccomment=None,
            members=[
                method
            ],
            conformances=[],
            access_level=access_level
        )
    
    def _proposeMethodGenerator(self, cName: str, args: c_ast.ParamList) -> MemberMethodGenerator | None:
        if len(args.params) < 1:
            return None
        
        for map in self.methodMappers:
            if cName.startswith(map.methodPrefix):
                return map
        
        return None
    
    def propose_conformances(self, decl: SwiftExtensionDecl) -> list[str] | None:
        result = []
        
        # Match required protocols
        for req in self.conformances:
            if decl.original_name is None:
                continue

            c_name = decl.original_name
            if req.symbolName != c_name:
                continue
            
            req.satisfied = True

            result.extend(req.conformances)
        
        return list(set(result))
    
    #

    def generate(self, node: c_ast.Node, context: c_ast.FileAST) -> SwiftDecl | None:
        match node:
            case c_ast.Enum():
                decl = self.generate_enum(node, context)
                if decl is None:
                    return None

                if self.symbol_filter.should_gen_enum_extension(node, decl):
                    return decl
                
            case c_ast.Struct():
                decl = self.generate_struct(node, context)
                if decl is None:
                    return None

                if self.symbol_filter.should_gen_struct_extension(node, decl):
                    return decl
                
            case c_ast.FuncDecl():
                fDecl = self.generate_funcDecl(node, context)
                if fDecl is None:
                    return None

                if self.symbol_filter.should_gen_funcDecl(node, fDecl):
                    return fDecl
        
        return None

    def generate_from_list(self, nodes: list[c_ast.Node], context: c_ast.FileAST) -> list[SwiftDecl]:
        result = []
        for node in nodes:
            decl = self.generate(node, context)
            if decl is not None:
                result.append(decl)

        return result

    def post_merge(self, decls: list[SwiftDecl]) -> list[SwiftDecl]:
        "Applies post-type merge operations to a list of Swift declarations"

        # Use proposed conformances to generate required members
        for decl in decls:
            if not isinstance(decl, SwiftExtensionDecl):
                continue
            if not isinstance(decl.original_node, c_ast.Struct):
                continue

            for conformance in sorted(decl.conformances):
                if gen := get_conformance_generator(conformance):
                    decl.members.extend(
                        gen.generate_members(decl, decl.original_node)
                    )

        return decls
