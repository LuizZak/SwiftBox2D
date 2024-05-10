# Requires Python 3.10

import argparse
import re
import sys

from pathlib import Path
from typing import Iterable

from pycparser import c_ast
from utils.cli.cli_printing import print_stage_name
from utils.cli.console_color import ConsoleColor
from utils.converters.default_symbol_name_formatter import DefaultSymbolNameFormatter
from utils.converters.swift_type_mapper import SwiftTypeMapper
from utils.converters.symbol_name_formatter import SymbolNameFormatter
from utils.cutils.cutils import declarationFromType
from utils.data.generator_config import GeneratorConfig
from utils.data.swift_decl_lookup import SwiftDeclLookup
from utils.data.swift_decls import (
    CDeclKind,
    SwiftAccessLevel,
    SwiftDecl,
    SwiftExtensionDecl,
    SwiftMemberFunctionDecl,
    SwiftMemberVarDecl,
)
from utils.data.swift_file import SwiftFile
from utils.directory_structure.directory_structure_manager import (
    DirectoryStructureEntry,
    DirectoryStructureManager,
)
from utils.doccomment.doccomment_block import DoccommentBlock
from utils.doccomment.doccomment_formatter import DoccommentFormatter
from utils.generator.known_conformance_generators import get_conformance_generator
from utils.generator.swift_decl_generator import SwiftDeclGenerator, coord_to_location
from utils.generator.symbol_generator_filter import SymbolGeneratorFilter
from utils.generator.symbol_name_generator import SymbolNameGenerator
from utils.data.compound_symbol_name import ComponentCase, CompoundSymbolName

from utils.generator.type_generator import (
    DeclGeneratorTarget,
    DeclFileGeneratorStdoutTarget,
    DeclFileGeneratorDiskTarget,
    TypeGeneratorRequest,
    generate_types,
)
from utils.paths import paths

CONFIG = """
{
    "declarations": {
        "prefixes": ["b2"],
        "functionsToMethods": [
            { "cPrefix": "b2World_", "swiftType": "B2World", "param0": { "swiftName": "id", "type": "b2WorldId" } },
            { "cPrefix": "b2Body_", "swiftType": "B2Body", "param0": { "swiftName": "id", "type": "b2BodyId" } },
            { "cPrefix": "b2Joint_", "swiftType": "B2Joint", "param0": { "swiftName": "id", "type": "b2JointId" } },
            { "cPrefix": "b2Shape_", "swiftType": "B2Shape", "param0": { "swiftName": "id", "type": "b2ShapeId" } },
            { "cPrefix": "b2Chain_", "swiftType": "B2Chain", "param0": { "swiftName": "id", "type": "b2ChainId" } }
        ],
        "structConformances": [
            { "cName": "b2Vec2", "conformances": ["Equatable", "Hashable", "CustomStringConvertible"] },
            { "cName": "b2Circle", "conformances": ["Equatable", "Hashable"] }
        ]
    },
    "symbolFormatting": {
        "capitalizeTerms": ["AABB"],
        "patternsToSplit": [],
        "snakeCaseAfterTerms": []
    },
    "docComments": {
        "collect": true
    },
    "fileGeneration": {
        "targetPath": "Sources/SwiftBox2D/Generated",
        "globalFileSuffix": "+Ext",
        "imports": ["box2d"]
    }
}
"""


class MemberMethodGenerator:
    methodPrefix: str
    classToMap: CompoundSymbolName
    firstArgumentMember: str
    firstArgumentType: str

    def __init__(self, methodPrefix: str, classToMap: CompoundSymbolName | str, firstArgumentMember: str, firstArgumentType: str):
        self.methodPrefix = methodPrefix
        if isinstance(classToMap, CompoundSymbolName):
            self.classToMap = classToMap
        else:
            self.classToMap = CompoundSymbolName.from_pascal_case(classToMap)
        self.firstArgumentMember = firstArgumentMember
        self.firstArgumentType = firstArgumentType

    def transform(
        self,
        typeMapper: SwiftTypeMapper,
        node: c_ast.FuncDecl,
        fName: CompoundSymbolName,
        context: c_ast.FileAST
    ) -> SwiftMemberFunctionDecl | None:

        if len(node.args.params) < 1:
            return None
        
        arguments: list[SwiftMemberFunctionDecl.ARG_TYPE] = list(map(
            lambda p: (None, declarationFromType(p.type)[0], typeMapper.mapToSwiftType(p.type, context).to_string()),
            node.args.params[1:]
        ))
        cCallArgs = [self.firstArgumentMember] + list(map(lambda a: a[1], arguments))

        return SwiftMemberFunctionDecl(
            c_kind=CDeclKind.FUNC,
            name=fName,
            original_name=CompoundSymbolName.from_pascal_case(node.type.declname),
            arguments=arguments,
            return_type=typeMapper.mapToSwiftType(node.type.type, context).to_string(),
            origin=coord_to_location(node.coord),
            original_node=node,
            doccomment=None,
            body=[
                f"{node.type.declname}({', '.join(cCallArgs)})"
            ]
        )


# MARK: Config

FILE_NAME = "box2d.h"

BOX2D_PREFIXES = [
    "b2",
]
"""
List of prefixes from Box2D declarations to convert

Will also be used as a list of terms to remove the prefix of in final declaration names.
"""

STRUCT_CONFORMANCES: list[tuple[str, list[str]]] = [
    # ("SomeStruct", ["Conformance1", "Conformance2", ...])
    ("b2Circle", ["Equatable", "Hashable"]),
    ("b2Vec2", ["Equatable", "Hashable", "CustomStringConvertible"]),
]
"""
List of pattern matching to apply to C struct declarations along with a list of
conformances that should be appended, in case the struct matches the pattern.
"""

# List of member method generators.
METHOD_MAPPERS: list[MemberMethodGenerator] = [
    MemberMethodGenerator("b2World", "B2World", "id", "b2WorldId"),
    MemberMethodGenerator("b2Body", "B2Body", "id", "b2BodyId"),
    MemberMethodGenerator("b2Joint", "B2Joint", "id", "b2JointId"),
    MemberMethodGenerator("b2Shape", "B2Shape", "id", "b2ShapeId"),
    MemberMethodGenerator("b2Chain", "B2Chain", "id", "b2ChainId"),
]

# MARK: Definitions

class Box2DDeclGenerator(SwiftDeclGenerator):
    # Lists declarations that where parsed and matched with an entry in STRUCT_CONFORMANCES.
    foundDecls: list[str] = []
    typeMapper = SwiftTypeMapper()

    def generate_funcDecl(self, node: c_ast.FuncDecl, context: c_ast.FileAST) -> SwiftDecl | None:
        funcName: str = node.type.declname
        if "_" not in funcName:
            return None
        (l, r) = funcName.split("_")
        transformer = self.mapTarget(l, node.args)
        if transformer is None:
            return None
        if not isinstance(node.type, c_ast.TypeDecl):
            return None

        fName = self.symbol_name_generator.generate_funcDecl_name(r)

        method = transformer.transform(self.typeMapper, node, fName, context)
        if method is None:
            return None

        return SwiftExtensionDecl(
            name=transformer.classToMap,
            original_name=None,
            origin=coord_to_location(node.coord),
            original_node=node,
            c_kind=CDeclKind.STRUCT,
            doccomment=None,
            members=[
                method
            ],
            conformances=[],
            access_level=SwiftAccessLevel.INTERNAL
        )
    
    def mapTarget(self, lead: str, args: c_ast.ParamList) -> MemberMethodGenerator | None:
        if len(args.params) < 1:
            return None
        
        for map in METHOD_MAPPERS:
            if map.methodPrefix == lead:
                return map
        return None

    def generate_enum(self, node: c_ast.Enum, context: c_ast.FileAST) -> SwiftExtensionDecl | None:
        decl = super().generate_enum(node, context)
        if decl is None:
            return decl

        return decl

    def generate_struct(self, node: c_ast.Struct, context: c_ast.FileAST) -> SwiftExtensionDecl | None:
        decl = super().generate_struct(node, context)

        if conformances := self.propose_conformances(decl):
            decl.conformances.extend(conformances)

        return decl
    
    def propose_conformances(self, decl: SwiftExtensionDecl) -> list[str] | None:
        result = []
        
        # Match required protocols
        for req in STRUCT_CONFORMANCES:
            c_name = decl.original_name.to_string()
            if req[0] != c_name:
                continue
            
            self.foundDecls.append(c_name)

            result.extend(req[1])
        
        return list(set(result))
    
    def post_merge(self, decls: list[SwiftDecl]) -> list[SwiftDecl]:
        result = super().post_merge(decls)

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

        return result


class Box2DSymbolFilter(SymbolGeneratorFilter):
    
    def should_gen_enum_extension(
        self, node: c_ast.Enum, decl: SwiftExtensionDecl
    ) -> bool:
        return False

    def should_gen_enum_var_member(
        self, node: c_ast.Enumerator, decl: SwiftMemberVarDecl
    ) -> bool:
        return False

    def should_gen_struct_extension(
        self, node: c_ast.Struct, decl: SwiftExtensionDecl
    ) -> bool:
        if node.name is None:
            return False
        for conformance in STRUCT_CONFORMANCES:
            if node.name == conformance[0]:
                return True
        return False
    
    def should_gen_funcDecl(
        self, node: c_ast.FuncDecl, decl: SwiftDecl
    ) -> bool:
        return True


class Box2DNameGenerator(SymbolNameGenerator):
    formatter: SymbolNameFormatter

    def __init__(self, formatter: DefaultSymbolNameFormatter):
        self.formatter = formatter
    
    @classmethod
    def from_config(cls, config: GeneratorConfig):
        return Box2DNameGenerator(
            formatter=DefaultSymbolNameFormatter.from_config(config.formatter)
        )

    def format_enum_case_name(self, name: CompoundSymbolName) -> CompoundSymbolName:
        """
        Fixes some wonky enum case name capitalizations.
        """
        name = self.formatter.format(name)
        result: list[CompoundSymbolName.Component] = name.components

        for i, comp in enumerate(result):
            if comp.string.startswith("Uint"):
                result[i] = comp.replacing_in_string("Uint", "UInt").with_string_case(
                    ComponentCase.AS_IS
                )

        return CompoundSymbolName(result)

    def generate(self, name: str) -> CompoundSymbolName:
        return CompoundSymbolName.from_pascal_case(name)

    def generate_enum_name(self, name: str) -> CompoundSymbolName:
        return self.generate(name)

    def generate_enum_case(
        self, enum_name: CompoundSymbolName, enum_original_name: str, case_name: str
    ) -> CompoundSymbolName:
        name = CompoundSymbolName.from_snake_case(case_name)

        orig_enum_name = CompoundSymbolName.from_snake_case(enum_original_name)

        (new_name, prefix) = name.removing_common(orig_enum_name, case_sensitive=False)
        new_name = new_name.camel_cased()

        if prefix is not None:
            prefix = prefix.camel_cased()
            new_name[0].joint_to_prev = "_"

            new_name = CompoundSymbolName(
                components=prefix.components + new_name.components
            )

        return self.format_enum_case_name(new_name)

    def generate_struct_name(self, name: str) -> CompoundSymbolName:
        return self.generate(name)

    def generate_original_enum_name(self, name: str) -> CompoundSymbolName:
        return self.generate(name)

    def generate_original_enum_case(self, case_name: str) -> CompoundSymbolName:
        return self.generate(case_name)

    def generate_original_struct_name(self, name: str) -> CompoundSymbolName:
        return self.generate(name)
    
    def generate_funcDecl_name(self, name: str) -> CompoundSymbolName:
        return self.formatter.format(self.generate(name).camel_cased())


class Box2DDoccommentFormatter(DoccommentFormatter):
    """
    Formats doc comments from Box2D to be more Swifty, including renaming \
    referenced C symbol names to the converted Swift names.
    """

    def __init__(self):
        self.ref_regex = re.compile(r"\\ref (\w+(?:\(\))?)", re.IGNORECASE)
        self.backtick_regex = re.compile(r"`([^`]+)`")
        self.backtick_word_regex = re.compile(r"\w+")
        self.backtick_cpp_member_regex = re.compile(r"(\w+)::(\w+)")

    def replace_refs(self, string: str) -> str:
        return self.ref_regex.sub(
            lambda match: f"`{''.join(match.groups())}`",
            string,
        )

    def convert_refs(self, string: str, lookup: SwiftDeclLookup) -> str:
        def convert_word_match(match: re.Match[str]) -> str:
            name = match.group()
            swift_name = lookup.lookup_c_symbol(name)
            if swift_name is not None:
                return swift_name

            return name

        def convert_backtick_match(match: re.Match[str]) -> str:
            replaced = self.backtick_word_regex.sub(
                convert_word_match,
                match.group(),
            )
            # Perform C++ symbol rewriting (Type::member)
            replaced = self.backtick_cpp_member_regex.sub(
                lambda m: f"{m.group(1)}.{m.group(2)}",
                replaced
            )
            
            return replaced

        return self.backtick_regex.sub(convert_backtick_match, string)

    def format_doccomment(
        self, comment: DoccommentBlock | None, decl: SwiftDecl, lookup: SwiftDeclLookup
    ) -> DoccommentBlock | None:
        if comment is None:
            return super().format_doccomment(comment, decl, lookup)
        
        lines = comment.lines()

        # Remove '\ingroup*' lines
        lines = filter(lambda c: not c.startswith("\\ingroup"), lines)

        # Reword '\note' to '- note'
        lines = map(lambda c: c.replace("\\note", "- note:"), lines)
        # Replace "\ref <symbol>" with "`<symbol>`"
        lines = map(self.replace_refs, lines)
        # Convert C symbol references to Swift symbols
        lines = map(lambda c: self.convert_refs(c, lookup), lines)

        return super().format_doccomment(comment.with_lines(lines), decl, lookup)


class Box2DDirectoryStructureManager(DirectoryStructureManager):
    def make_declaration_files(self, decls: Iterable[SwiftDecl]) -> list[SwiftFile]:
        result = super().make_declaration_files(decls)
        for file in result:
            file.header_lines.append(
                f"// Generated by {Path(__file__).relative_to(paths.SOURCE_ROOT_PATH)}"
            )

        return result

    def path_matchers(self) -> list[DirectoryStructureEntry]:
        # Array of tuples containing:
        # tuple.0: An array of path components (min 1, must not have special characters);
        # tuple.1: Either a regular expression, OR a list of regular expression/exact
        #          strings that file names will be tested against.
        # Matches are made against full file names, with no directory information,
        # e.g.: "BLContext.swift", "BLFillRule.swift", "BLResultCode.swift", etc.
        return [
            # Ex:
            # (
            #     ["Folder"],
            #     [
            #         re.compile(r"^SomePrefix.+"),
            #         "AFileName.swift",
            #         ...
            #     ]
            # ),
        ]


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Generates .swift files for Box2D enum and struct declarations."
    )

    parser.add_argument(
        "-c",
        "--config_file",
        type=Path,
        default=Path("generate_types.json"),
        help="""
        Path to JSON file containing the configuration for the type generation.
        If not provided, defaults to 'generate_types.json'.
        """
    )
    parser.add_argument(
        "--stdout",
        action="store_true",
        help="Outputs files to stdout instead of file disk.",
    )
    parser.add_argument(
        "-o",
        "--output",
        dest="path",
        type=Path,
        help="Path to put generated files on",
    )

    args = parser.parse_args()

    input_path = paths.scripts_path(FILE_NAME)
    if not input_path.exists() or not input_path.is_file():
        print("Error: Expected path to an existing header file within utils/.")
        return 1

    swift_target_path = (
        args.path
        if args.path is not None
        else paths.srcroot_path("Sources", "SwiftBox2D", "Generated")
    )
    if not swift_target_path.exists() or not swift_target_path.is_dir():
        print(f"Error: No target directory with name '{swift_target_path}' found.")
        return 1

    destination_path = swift_target_path
    
    config = GeneratorConfig.from_json_file(args.config_file)

    target: DeclGeneratorTarget

    if args.stdout:
        target = DeclFileGeneratorStdoutTarget()
    else:
        target = DeclFileGeneratorDiskTarget(destination_path, rm_folder=True)

    print_stage_name(f"Loaded config from {ConsoleColor.CYAN(args.config_file)}")

    symbol_filter = SymbolGeneratorFilter.from_config(config.declarations.filters)
    symbol_name_generator = Box2DNameGenerator.from_config(config)
    decl_generator = Box2DDeclGenerator(
        prefixes=config.declarations.prefixes,
        symbol_filter=symbol_filter,
        symbol_name_generator=symbol_name_generator,
    )
    request = TypeGeneratorRequest.from_config(
        config=config,
        header_file=input_path,
        target=target,
        swift_decl_generator=decl_generator,
        symbol_filter=symbol_filter,
        symbol_name_generator=symbol_name_generator,
        doccomment_formatter=Box2DDoccommentFormatter(),
        directory_manager=Box2DDirectoryStructureManager.from_config(config.fileGeneration),
    )

    generate_types(request)

    # Warn about entries in STRUCT_CONFORMANCES that where not matched
    expectedDecls = set(map(lambda t: t[0], STRUCT_CONFORMANCES))
    missingDecls = expectedDecls.symmetric_difference(decl_generator.foundDecls)

    for decl in missingDecls:
        print(f"{ConsoleColor.YELLOW('WARNING')}: Declaration {ConsoleColor.CYAN(decl)} listed in {ConsoleColor.CYAN('STRUCT_CONFORMANCES')} was not matched by any generated declaration!")


if __name__ == "__main__":
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        sys.exit(1)
