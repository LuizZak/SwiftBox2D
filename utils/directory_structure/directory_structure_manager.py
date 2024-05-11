from dataclasses import dataclass
import re
from pathlib import Path
from typing import List, Iterable

from utils.data.generator_config import GeneratorConfig
from utils.data.swift_decls import SwiftDecl
from utils.data.swift_file import SwiftFile

DirectoryStructureEntry = tuple[list[str], str | re.Pattern | list[str | re.Pattern]]

def escape_path_component(pathComponent: str) -> str:
    """
    Removes/replaces any character in a path component (such as a folder name
    or file name), restricting the character selection to the ones that match
    the regex: `[\\w_. -+]`, replacing any such character with `_`.
    """
    # Reject parent directory paths
    if pathComponent == "..":
        return "_"

    return re.sub(r"[^\w_. -+]", "_", pathComponent)


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

        pathComponents: list[str]
        "Path components (min 1, must not have special characters)"

        patterns: list[re.Pattern | str]
        "List of regex patterns or full file names to be matched to this entry's directory"

        @classmethod
        def from_config(cls, config: GeneratorConfig.FileGeneration.DirectoryStructureEntry):
            def parse_pattern(value: str):
                if value.startswith("/") and value.endswith("/"):
                    return re.compile(value[1:-1], re.IGNORECASE)
                return value
            
            splitPath = Path(config.path).parts
            patterns = map(parse_pattern, config.patterns)

            return cls(
                pathComponents=list(map(escape_path_component, splitPath)),
                patterns=list(patterns)
            )
    
    basePath: Path
    "Base path to generate files to."

    globalFileSuffix: str
    """
    A file suffix to append to all Swift files generated.
    This is added before the .swift file extension.
    """
    pathMatchers: list[DirectoryStructureEntry]

    def __init__(
        self,
        basePath: Path,
        globalFileSuffix: str | None = None,
        pathMatchers: Iterable[DirectoryStructureEntry] | None = None
    ):
        self.basePath = basePath
        self.globalFileSuffix = globalFileSuffix if globalFileSuffix is not None else ""
        self.pathMatchers = list(pathMatchers) if pathMatchers is not None else []
    
    @classmethod
    def from_config(cls, config: GeneratorConfig.FileGeneration):
        return cls(
            basePath=Path.absolute(Path(config.targetPath)),
            globalFileSuffix=config.globalFileSuffix,
            pathMatchers=map(cls.DirectoryStructureEntry.from_config, config.directoryStructure)
        )

    def path_matchers(self) -> list[DirectoryStructureEntry]:
        return self.pathMatchers

    def make_declaration_files(self, decls: Iterable[SwiftDecl]) -> list[SwiftFile]:
        result: dict[Path, SwiftFile] = dict()

        for decl in decls:
            path = self.path_for_decl(decl)
            file = result.get(path, SwiftFile(path, [], []))
            file.add_decl(decl)

            result[path] = file

        return list(result.values())

    def path_for_decl(self, decl: SwiftDecl) -> Path:
        file_path = self.file_for_decl(decl)

        return file_path

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

        dir_path = self.basePath
        longest_path: List[str] = []

        for matcher in self.path_matchers():
            if not matches(matcher.patterns, file_name):
                continue

            if len(matcher.pathComponents) > len(longest_path):
                longest_path = matcher.pathComponents

        for component in longest_path:
            if not component.isalnum():
                raise Exception(
                    f"Expected suggested paths to contain only alphanumeric values for file {file_name}, found {component} (full: {longest_path})"
                )

        return dir_path.joinpath(*map(escape_path_component, longest_path))

    def file_for_decl(self, decl: SwiftDecl) -> Path:
        file_name = self.file_name_for_decl(decl)

        return self.folder_for_file(file_name).joinpath(file_name)

    def file_name_for_decl(self, decl: SwiftDecl) -> str:
        return escape_path_component(f"{decl.name.to_string()}{self.globalFileSuffix}.swift")
