# Utility to extract Swift-styled aliases of DirectX C types.

import sys
import os
import subprocess
import shutil
from dataclasses import dataclass
import time
from typing import Generator

import pycparser

from pathlib import Path
from pycparser import c_ast
from contextlib import contextmanager
from utils.cli.cli_printing import print_stage_name
from utils.cli.console_color import ConsoleColor

from utils.converters.syntax_stream import SyntaxStream
from utils.data.generator_config import GeneratorConfig
from utils.data.swift_decl_lookup import SwiftDeclLookup
from utils.data.swift_decl_visitor import SwiftDeclVisitor
from utils.doccomment.doccomment_formatter import DoccommentFormatter
from utils.doccomment.doccomment_manager import DoccommentManager
from utils.generators.swift_decl_merger import SwiftDeclMerger
from utils.generators.swift_decl_generator import SwiftDeclGenerator
from utils.generators.symbol_generator_filter import SymbolGeneratorFilter
from utils.generators.symbol_name_generator import SymbolNameGenerator
from utils.data.swift_decls import (
    SwiftDecl,
    SwiftDeclVisitResult,
)
from utils.directory_structure.directory_structure_manager import (
    DirectoryStructureManager,
)
from utils.data.swift_file import SwiftFile

# Utils
from utils.paths import paths


def run_cl(input_path: Path) -> bytes:
    args: list[str | os.PathLike] = [
        "cl",
        "/E",
        "/Za",
        "/Zc:wchar_t",
        input_path,
    ]

    return subprocess.check_output(args, cwd=paths.SCRIPTS_ROOT_PATH)


def run_clang(input_path: Path) -> bytes:
    args: list[str | os.PathLike] = [
        "clang",
        "-E",
        "-fuse-line-directives",
        "-std=c99",
        "-pedantic-errors",
        input_path,
    ]

    return subprocess.check_output(args, cwd=paths.SCRIPTS_ROOT_PATH)


def run_c_preprocessor(input_path: Path) -> bytes:
    if sys.platform == "win32":
        return run_cl(input_path)

    return run_clang(input_path)


class DeclGeneratorTarget:
    def prepare(self):
        pass

    @contextmanager
    def create_stream(self, _: Path) -> Generator:
        raise NotImplementedError("Must be overridden by subclasses.")


class DeclFileGeneratorDiskTarget(DeclGeneratorTarget):
    def __init__(
        self, destination_folder: Path, rm_folder: bool = True, verbose: bool = True
    ):
        self.destination_folder = destination_folder
        self.rm_folder = rm_folder
        self.directory_manager = DirectoryStructureManager(destination_folder)
        self.verbose = verbose

    def prepare(self):
        if self.verbose:
            print(
                f"Generating .swift files to {ConsoleColor.MAGENTA(self.destination_folder)}..."
            )

        if self.rm_folder:
            shutil.rmtree(self.destination_folder)
            os.mkdir(self.destination_folder)

    @contextmanager
    def create_stream(self, path: Path) -> Generator:
        path.parent.mkdir(parents=True, exist_ok=True)

        with open(path, "w", newline="\n") as file:
            stream = SyntaxStream(file)
            yield stream


class DeclFileGeneratorStdoutTarget(DeclGeneratorTarget):
    @contextmanager
    def create_stream(self, path: Path) -> Generator:
        stream = SyntaxStream(sys.stdout)
        stream.write_then_line(f"[Create file at: {ConsoleColor.CYAN(path.resolve())}]")
        yield stream


class DeclFileGenerator:
    def __init__(
        self,
        destination_folder: Path,
        target: DeclGeneratorTarget,
        decls: list[SwiftDecl],
        includes: list[str],
        directory_manager: DirectoryStructureManager,
        verbose: bool = False,
    ):
        self.directory_manager = directory_manager
        self.destination_folder = destination_folder
        self.target = target
        self.decls = decls
        self.includes = includes
        self.verbose = verbose

    def generate_file(self, file: SwiftFile):
        with self.target.create_stream(file.path) as stream:
            file.write(stream)

    def generate(self):
        self.target.prepare()

        files = self.directory_manager.make_declaration_files(self.decls)

        for file in files:
            file.includes = self.includes
            self.generate_file(file)

            if self.verbose:
                rel_path = file.path.relative_to(self.destination_folder)
                print(
                    f"Generated {ConsoleColor.MAGENTA(rel_path)} with {ConsoleColor.CYAN(len(file.decls))} declaration(s)"
                )


# noinspection PyPep8Naming
class DeclCollectorVisitor(c_ast.NodeVisitor):
    decls: list[c_ast.Node] = []

    def __init__(self, prefixes: list[str]):
        self.prefixes = prefixes

    def should_include(self, decl_name: str) -> bool:
        for prefix in self.prefixes:
            if decl_name.startswith(prefix):
                return True

        return False

    def visit_Struct(self, node: c_ast.Struct):  # noqa: N802
        if node.name is not None and self.should_include(node.name):
            self.decls.append(node)

    def visit_Enum(self, node: c_ast.Enum):  # noqa: N802
        if node.name is not None and self.should_include(node.name):
            self.decls.append(node)

    def visit_FuncDecl(self, node: c_ast.FuncDecl):  # noqa: N802
        ident = self.identifier_from_type(node.type)
        if ident is None:
            return

        if ident is not None and self.should_include(ident):
            self.decls.append(node)

    def identifier_from_type(self, decl: c_ast.Decl) -> str | None:
        if not isinstance(decl, c_ast.TypeDecl):
            return None

        return decl.declname


class SwiftDoccommentFormatterVisitor(SwiftDeclVisitor):
    def __init__(self, formatter: DoccommentFormatter, lookup: SwiftDeclLookup):
        self.formatter = formatter
        self.lookup = lookup

    def generic_visit(self, decl: SwiftDecl) -> SwiftDeclVisitResult:
        decl.doccomment = self.formatter.format_doccomment(
            decl.doccomment, decl, self.lookup
        )

        return SwiftDeclVisitResult.VISIT_CHILDREN


@dataclass
class TypeGeneratorRequest:
    header_file: Path
    destination: Path
    prefixes: list[str]
    target: DeclGeneratorTarget
    includes: list[str]
    symbol_filter: SymbolGeneratorFilter
    symbol_name_generator: SymbolNameGenerator
    doccomment_manager: DoccommentManager
    directory_manager: DirectoryStructureManager
    swift_decl_generator: SwiftDeclGenerator

    @classmethod
    def from_config(
        cls,
        config: GeneratorConfig,
        header_file: Path,
        target: DeclGeneratorTarget,
        file_header: str = "",
    ):
        destination = Path.absolute(Path(config.file_generation.target_path))
        prefixes = config.declarations.prefixes
        includes = config.file_generation.imports
        directory_manager = DirectoryStructureManager.from_config(
            config.file_generation
        )

        if len(file_header) > 0:
            directory_manager.global_header_lines.append(file_header)

        return cls(
            header_file=header_file,
            destination=destination,
            prefixes=prefixes,
            target=target,
            includes=includes,
            directory_manager=directory_manager,
            symbol_filter=SymbolGeneratorFilter.from_config(config.declarations),
            symbol_name_generator=SymbolNameGenerator.from_config(config.declarations),
            swift_decl_generator=SwiftDeclGenerator.from_config(config.declarations),
            doccomment_manager=DoccommentManager.from_config(config.doc_comments),
        )


def _label_time_ns(ns):
    def format(value, suffix):
        return f"{value:0.3f}{suffix}"

    delta = ns
    if delta < 1000:  # ns -> us
        return format(delta, "ns")
    delta /= 1000
    if delta < 1000:  # us -> ms
        return format(delta, "us")
    delta /= 1000
    if delta < 1000:  # ms -> s
        return format(delta, "ms")

    seconds = ns / 1000000000
    days, seconds = divmod(seconds, 86400)
    hours, seconds = divmod(seconds, 3600)
    minutes, seconds = divmod(seconds, 60)
    ms = (ns // 1000000) % 1000

    if days > 0:
        return "%dd%dh%dm%d.%ds" % (days, hours, minutes, seconds, ms)
    elif hours > 0:
        return "%dh%dm%d.%ds" % (hours, minutes, seconds, ms)
    elif minutes > 0:
        return "%dm%d.%ds" % (minutes, seconds, ms)
    else:
        return "%d.%ds" % (seconds, ms)


def generate_types(request: TypeGeneratorRequest) -> int:
    start = time.perf_counter_ns()
    result = _generate_types(request)
    duration = time.perf_counter_ns() - start

    print(f"Completed request in: {_label_time_ns(duration)}")

    return result


def _generate_types(request: TypeGeneratorRequest) -> int:
    print_stage_name("Generating header file...")

    output_file = run_c_preprocessor(request.header_file)

    # Windows-specific fix to replace some page feeds that are present in the original system headers
    if sys.platform == "win32":
        output_file = output_file.replace(b"\x0c", b"")

    output_path = request.header_file.with_suffix(".i")
    with open(output_path, "wb") as f:
        f.write(output_file)

    print_stage_name("Parsing generated header file...")

    ast = pycparser.parse_file(output_path, use_cpp=False)

    print_stage_name("Collecting Swift symbol candidates...")

    visitor = DeclCollectorVisitor(prefixes=request.prefixes)
    visitor.visit(ast)

    decl_generator = request.swift_decl_generator
    swift_decls = decl_generator.generate_from_list(visitor.decls, ast)

    print(f"Found {ConsoleColor.CYAN(len(swift_decls))} potential declarations")

    if request.doccomment_manager.should_collect:
        print_stage_name("Generating doc comments...")
        request.doccomment_manager.populate(swift_decls)

    print_stage_name("Merging generated Swift type declarations...")

    merger = SwiftDeclMerger()
    swift_decls = merger.merge(swift_decls)

    print(f"Merged down to {ConsoleColor.CYAN(len(swift_decls))} declarations")

    swift_decls = decl_generator.post_merge(swift_decls)

    if request.doccomment_manager.should_format:
        print_stage_name("Formatting doc comments...")

        request.doccomment_manager.format(swift_decls)

    print_stage_name("Generating files...")

    generator = DeclFileGenerator(
        request.destination,
        request.target,
        swift_decls,
        request.includes,
        request.directory_manager,
        verbose=True,
    )
    generator.generate()

    # Warn about entries in type protocol conformance entries that where not matched
    # against a type
    for conformance in decl_generator.conformances:
        if conformance.satisfied:
            continue

        print(
            f"{ConsoleColor.YELLOW('WARNING')}: Declaration {ConsoleColor.CYAN(conformance.symbol_name)} listed in configuration was not matched by any generated declaration!"
        )

    print(ConsoleColor.GREEN("Success!"))

    return 0
