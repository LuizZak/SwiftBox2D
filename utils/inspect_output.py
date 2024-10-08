# Allows inspection of #include trees in box2d.i file.
# Usage:
#
#     python inspect_output.py absolute <line-number>
# Or:
#     python inspect_output.py relative <included-header-file-name> <line-number-in-included-header>
#
# All relevant #line directives preceding the given line which number will be printed.
#
# If line is relative to an included file, the line number from #line directives will
# be respected when searching for the relative line number in the absolute file.
#
# Sample usage:
#
# > python utils/inspect_output.py --file utils/box2d.i relative stdarg.h 14
# box2d.h:21 (@ utils/box2d.i:8)
# box2d.h:46 (@ utils/box2d.i:10)
# api.h:15 (@ utils/box2d.i:12)
# stdarg.h:14 (@ utils/box2d.i:14)
#

import argparse
import os
import re
from pathlib import Path
from typing import Callable, List, Optional, TypeVar

from cli.console_color import ConsoleStyle, colored

T = TypeVar("T")


def find(predicate: Callable[[T], bool], list: List[T]) -> Optional[int]:
    for i, item in enumerate(list):
        if predicate(item):
            return i

    return None


class FileVisit(object):
    def __init__(self, file_path: Path, line: int, absolute_line: int):
        self.file_path = file_path
        self.line = line
        self.absolute_line = absolute_line

    def __str__(self) -> str:
        return f"{self.file_path.name}:{self.line} (@ {self.absolute_line})"


class FileWalker(object):
    def __init__(self, file_name: Path):
        self.visits: List[FileVisit] = []
        self.file_name = file_name
        self.pattern = re.compile(r"#line\s+(\d+)\s+\"(.+)\"")

    def process_line(
        self, line_contents: str, absolute_line: int
    ) -> Optional[FileVisit]:
        match = self.pattern.match(line_contents)
        if match is None:
            return None

        line = int(match.group(1))
        file = Path(match.group(2))
        if not file.is_absolute():
            file = Path.cwd().joinpath(file)

        visit = FileVisit(file, line - 1, absolute_line)

        self.visits.append(visit)

        return visit

    def walk_to_relative(self, target_file_name: str, target_line_number: int) -> bool:
        is_absolute = Path(target_file_name).is_absolute()
        target_file_name_resolved = Path(target_file_name).resolve()

        self.visits = []

        current_visit = FileVisit(self.file_name, 1, 1)

        with open(self.file_name, "r") as file:
            for line, line_contents in enumerate(file):
                visit = self.process_line(line_contents, line + 1)
                if visit is not None:
                    current_visit = visit
                else:
                    current_visit.line += 1
                    current_visit.absolute_line += 1

                if is_absolute:
                    paths_match = (
                        Path(current_visit.file_path).resolve()
                        == target_file_name_resolved
                    )
                else:
                    paths_match = current_visit.file_path.name == target_file_name

                if paths_match and current_visit.line == target_line_number:
                    return True

        return False

    def walk_to_absolute(self, target_line_number):
        self.visits = []

        with open(self.file_name, "r") as file:
            for line, line_contents in enumerate(file):
                if line >= target_line_number:
                    return

                visit = self.process_line(line_contents, line + 1)
                if visit is not None:
                    current_visit = visit
                else:
                    current_visit.line += 1
                    current_visit.absolute_line += 1

    def min_visits(self) -> list[FileVisit]:
        """
        Returns a reduced visit list where each element is the latest occurrence
        of a file name on the input file.
        The list is the minimal #line information needed to reconstruct the path
        of #include files on a preprocessed header file.
        """

        result: list[FileVisit] = []

        if len(self.visits) == 0:
            return result

        visit_stack: list[FileVisit] = []

        for visit in self.visits:
            index = find(lambda x: x.file_path == visit.file_path, visit_stack)

            if index is not None:
                visit_stack = visit_stack[0:index]

            visit_stack.append(visit)

        return visit_stack


def pretty_path(path: Path, line: int | None = None) -> str:
    if len(path.parts) == 1:
        contents = path.name
    else:
        contents = (
            f"{colored(path.parent, style=ConsoleStyle.FAINT)}{os.sep}{path.name}"
        )
    if line is not None:
        contents += f":{colored(line, style=ConsoleStyle.BOLD)}"
    return contents


def file_has_line_number(path: Path, line: int) -> bool:
    with open(path, "r") as file:
        for _ in range(line):
            if file.readline() == "":
                return False

    return True


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Allows inspection of #include trees in a pre-processed C header file."
    )

    parser.add_argument(
        "--file",
        dest="file_name",
        type=str,
        default="box2d.i",
        help="File to inspect. Defaults to 'box2d.i' if not provided.",
    )
    parser.add_argument(
        "--full-paths",
        dest="full_paths",
        action="store_true",
        help="Whether to print full file paths in #line directive readings.",
    )

    subparsers = parser.add_subparsers(dest="command")

    # absolute line
    absolute_parser = subparsers.add_parser(
        "absolute", help="Inspects the input file by line number directly."
    )
    absolute_parser.add_argument(
        "line_number", type=int, help="Inspects up to a given line number then stops."
    )

    # relative line
    relative_parser = subparsers.add_parser(
        "relative",
        help="Inspects the input file by a relative .h file and line number, as dictated by #line directives. Path can either be a filename+ext format, or a full path to compare to.",
    )
    relative_parser.add_argument(
        "relative_file_name",
        type=str,
        help="File name and extension of file to search for in #line directives.",
    )
    relative_parser.add_argument(
        "line_number",
        type=int,
        help="A line number of the file to search for. The line number starts counting by the line number in the #line directive of the respective filename.",
    )

    args = parser.parse_args()

    walker = FileWalker(Path.cwd().joinpath(Path(args.file_name)))

    if args.command is None:
        print("Error: Command name required.")
        parser.print_help()
        exit(1)

    if args.command == "absolute":
        walker.walk_to_absolute(args.line_number)
    elif args.command == "relative":
        if not walker.walk_to_relative(args.relative_file_name, args.line_number):
            file_path = Path(args.relative_file_name)
            print(
                f'Did not find file "{pretty_path(file_path)}" line {args.line_number}'
                + "\nIt is possible the line was elided by the pre-processor because it contained comments and/or pre-processor directives."
            )
            exit(1)
    else:
        print(f'Error: Unrecognized command "{args.command}"')
        exit(1)

    file_visits = walker.min_visits()

    depth = 0
    for visit in file_visits:
        if args.full_paths:
            file_name = visit.file_path.resolve()
        else:
            file_name = Path(visit.file_path.name)

        if depth == 0:
            indent = ""
        else:
            indent = ("   " * (depth - 1)) + "└─ "
        depth += 1

        print(
            f"{indent}{pretty_path(file_name, visit.line)} (@ {pretty_path(Path(args.file_name), visit.absolute_line)})"
        )
