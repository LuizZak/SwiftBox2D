from dataclasses import dataclass
import re
from pathlib import Path
from typing import List, Iterable

from utils.data.generator_config import GeneratorConfig
from utils.data.swift_decls import SwiftDecl
from utils.data.swift_file import SwiftFile

DirectoryStructureEntry = tuple[list[str], str | re.Pattern | list[str | re.Pattern]]


def escape_path_component(path_component: str) -> str:
    """
    Removes/replaces any character in a path component (such as a folder name
    or file name), restricting the character selection to the ones that match
    the regex: `[\\w_. -+]`, replacing any such character with `_`.
    """
    # Reject parent directory paths
    if path_component == "..":
        return "_"

    return re.sub(r"[^\w_. -+]", "_", path_component)


class DirectoryStructureManager:
    """
    A class that is used to manage nested directory structures for generated types.
    """

    @dataclass
    class DirectoryStructureEntry:
        """
        A directory entry that is used to redirect certain files into subfolders.
        Matches are made against full file names, with no directory information.
        """

        path_components: list[str]
        "Path components (min 1, must not have special characters)"

        patterns: list[re.Pattern | str]
        "List of regex patterns or full file names to be matched to this entry's directory"

        @classmethod
        def from_config(
            cls, config: GeneratorConfig.FileGeneration.DirectoryStructureEntry
        ):
            def parse_pattern(value: str):
                if value.startswith("/") and value.endswith("/"):
                    return re.compile(value[1:-1], re.IGNORECASE)
                return value

            split_path = Path(config.path).parts

            return cls(
                path_components=[escape_path_component(c) for c in split_path],
                patterns=[parse_pattern(p) for p in config.patterns],
            )

    base_path: Path
    "Base path to generate files to."

    global_file_suffix: str
    """
    A file suffix to append to all Swift files generated.
    This is added before the .swift file extension.
    """
    path_matchers: list[DirectoryStructureEntry]

    global_header_lines: list[str]
    "A list of lines to append to the top of every generated file."

    def __init__(
        self,
        base_path: Path,
        global_file_suffix: str | None = None,
        path_matchers: Iterable[DirectoryStructureEntry] | None = None,
    ):
        self.base_path = base_path
        self.global_file_suffix = (
            global_file_suffix if global_file_suffix is not None else ""
        )
        self.path_matchers = list(path_matchers) if path_matchers is not None else []
        self.global_header_lines = []

    @classmethod
    def from_config(cls, config: GeneratorConfig.FileGeneration):
        return cls(
            base_path=Path.absolute(Path(config.target_path)),
            global_file_suffix=config.global_file_suffix,
            path_matchers=map(
                cls.DirectoryStructureEntry.from_config, config.directory_structure
            ),
        )

    def make_declaration_files(self, decls: Iterable[SwiftDecl]) -> list[SwiftFile]:
        """Merges a given list of declarations into Swift files."""

        result: dict[Path, SwiftFile] = dict()

        for decl in decls:
            path = self.path_for_decl(decl)

            if (file := result.get(path)) is None:
                file = SwiftFile(path, [], [])
                file.header_lines.extend(self.global_header_lines)

            file.add_decl(decl)

            result[path] = file

        return list(result.values())

    def path_for_decl(self, decl: SwiftDecl) -> Path:
        file_path = self.file_for_decl(decl)

        return file_path

    def file_for_decl(self, decl: SwiftDecl) -> Path:
        file_name = self.file_name_for_decl(decl)

        return self.folder_for_file(file_name).joinpath(file_name)

    def file_name_for_decl(self, decl: SwiftDecl) -> str:
        return escape_path_component(
            f"{decl.name.to_string()}{self.global_file_suffix}.swift"
        )

    def folder_for_file(self, file_name: str) -> Path:
        def matches(
            pattern: str | re.Pattern | list[str | re.Pattern],
            file_name: str,
        ) -> bool:
            if isinstance(pattern, re.Pattern):
                if not pattern.match(file_name):
                    return False

                return True

            for pat in pattern:
                if isinstance(pat, str):
                    if pat == file_name:
                        return True
                    else:
                        continue
                if isinstance(pat, list):
                    return True if file_name in pat else False
                elif pat.match(file_name):
                    return True

            return False

        dir_path = self.base_path
        longest_path: List[str] = []

        for matcher in self.path_matchers:
            if not matches(matcher.patterns, file_name):
                continue

            if len(matcher.path_components) > len(longest_path):
                longest_path = matcher.path_components

        for component in longest_path:
            if not component.isalnum():
                raise Exception(
                    f"Expected suggested paths to contain only alphanumeric values for file {file_name}, found {component} (full: {longest_path})"
                )

        return dir_path.joinpath(*(escape_path_component(c) for c in longest_path))
