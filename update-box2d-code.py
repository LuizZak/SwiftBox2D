# Requires Python 3.10

import argparse
import glob
import os
import shutil
import subprocess
import sys
import stat

from typing import Callable
from pathlib import Path
from os import PathLike

from utils.cli.cli_printing import print_stage_name
from utils.cli.console_color import ConsoleColor


# List of glob patterns to remove from the Box2D folders after code is initially
# cloned.
rmFilePatterns: list[str] = [
    "**/CMakeLists.txt",
    "**/*.natvis",
    "**/*.h.in",
]


# -----
# Utility functions
# -----


def echo_call(bin: PathLike | str, *args: str):
    print(">", str(bin), *args)


def run(
    bin_name: str,
    *args: str,
    cwd: str | Path | None = None,
    echo: bool = True,
    silent: bool = False,
):
    if echo:
        echo_call(bin_name, *args)

    if silent:
        subprocess.check_output([bin_name] + list(args), cwd=cwd)
    else:
        subprocess.check_call([bin_name] + list(args), cwd=cwd)


def git(command: str, *args: str, cwd: str | Path | None = None, echo: bool = True):
    run("git", command, *args, cwd=cwd, echo=echo)


def git_output(*args: str, cwd: str | None = None, echo: bool = True) -> str:
    if echo:
        echo_call("git", *args)

    return subprocess.check_output(["git"] + list(args), cwd=cwd).decode("UTF8")


def path(root: PathLike | str, *args: PathLike | str) -> Path:
    return Path(root).joinpath(*args)


def cwd_path(*args: PathLike | str) -> Path:
    return path(Path.cwd(), *args)


# From: https://github.com/gitpython-developers/GitPython/blob/ea43defd777a9c0751fc44a9c6a622fc2dbd18a0/git/util.py#L101
# Windows has issues deleting readonly files that git creates
def git_rmtree(path_to_remove: os.PathLike) -> None:
    """Remove the given recursively.
    :note: we use shutil rmtree but adjust its behaviour to see whether files that
        couldn't be deleted are read-only. Windows will not remove them in that case"""

    def onerror(func: Callable, p: os.PathLike, _) -> None:
        # Is the error an access error ?
        os.chmod(p, stat.S_IWUSR)

        try:
            func(p)  # Will scream if still not possible to delete.
        except Exception:
            raise

    return shutil.rmtree(path_to_remove, False, onerror)


# ----
# Main logic
# ----

BOX2D_REPO = "https://github.com/erincatto/box2d.git"

BOX2D_TARGET_PATH = cwd_path("Sources", "box2d")

TEMP_FOLDER_NAME = "temp"


def create_temporary_folder() -> Path:
    temp_path = cwd_path(TEMP_FOLDER_NAME)
    if temp_path.exists():
        git_rmtree(temp_path)

    os.mkdir(temp_path)

    return temp_path


def remove_files_with_pattern(base_folder: Path, patterns: list[str]):
    for pattern in patterns:
        for result in glob.iglob(pattern, root_dir=base_folder, recursive=True):
            rel_path = os.path.relpath(Path(base_folder, result), base_folder)
            final_path = Path(base_folder, rel_path).resolve()

            if not str(final_path).startswith(str(base_folder.resolve())):
                continue

            print(f"{ConsoleColor.RED('rm')} {final_path}")
            os.remove(final_path)


def clone_repo(tag_or_branch: str | None, repo: str, clone_path: str):
    if tag_or_branch is None:
        git("clone", repo, "--depth=1", clone_path)
    else:
        git("clone", repo, clone_path)
        git("checkout", tag_or_branch, cwd=clone_path)


def clone_box2d(tag_or_branch: str | None, base_folder: Path) -> Path:
    print_stage_name("Cloning Box2D...")

    box2d_clone_path = str(path(base_folder, "box2d").absolute())

    clone_repo(tag_or_branch, BOX2D_REPO, box2d_clone_path)

    return Path(box2d_clone_path)


def backup_includes(from_path: Path, to_path: Path):
    if to_path.exists():
        shutil.rmtree(to_path)

    shutil.copytree(from_path, to_path)


def update_includes(include_path: Path, target_path: Path):
    old_includes = target_path.joinpath("include", "box2d")
    new_includes = include_path.joinpath("box2d")

    shutil.rmtree(old_includes)
    shutil.copytree(new_includes, old_includes)


def copy_repo_files(source_files: Path, include_path: Path, target_path: Path):
    # Update includes
    update_includes(include_path, target_path)

    # Backup includes before removing all files from Sources/box2d
    include_target_path = target_path.joinpath("include")
    include_backup_path = source_files.joinpath("include")
    backup_includes(include_target_path, include_backup_path)

    # Erase files and copy over
    shutil.rmtree(target_path)
    shutil.copytree(source_files, target_path)


def copy_box2d_files(src_path: Path, include_path: Path, target_path: Path):
    print_stage_name("Copying over Box2D files...")

    copy_repo_files(src_path, include_path, target_path)


def update_code(box2d_tag_or_branch: str | None, force: bool) -> int:
    if (not force) and len(git_output("status", "--porcelain", echo=False).strip()) > 0:
        print(
            ConsoleColor.RED(
                "Current git repo's state is not committed! Please commit and try again. (override with --force)"
            )
        )
        return 1

    # Create temp path
    temp_path = create_temporary_folder()

    # Clone
    box2d_clone_path = clone_box2d(box2d_tag_or_branch, temp_path)
    src_path = box2d_clone_path.joinpath("src")
    include_path = box2d_clone_path.joinpath("include")

    print_stage_name("Removing extraneous files...")
    remove_files_with_pattern(box2d_clone_path, rmFilePatterns)

    # Copy files
    copy_box2d_files(src_path, include_path, BOX2D_TARGET_PATH)

    print(ConsoleColor.GREEN("Success!"))

    git_status = git_output("status", "--porcelain").strip()
    if len(git_status) > 0:
        print(ConsoleColor.YELLOW("New unstaged changes:"))
        print(git_status)

    git_rmtree(temp_path)

    return 0


# -----
# Entry point
# -----


def main() -> int:
    def make_argparser() -> argparse.ArgumentParser:
        argparser = argparse.ArgumentParser()
        argparser.add_argument(
            "-b",
            "--box2d_tag",
            type=str,
            help="A tag or branch to clone from the Box2D repository. If not provided, defaults to latest commit of default branch.",
        )
        argparser.add_argument(
            "-f",
            "--force",
            action="store_true",
            help="Whether to ignore non-committed state of the repository. By default, the script fails if the repository has changes that are not committed to avoid conflicts and unintended changes.",
        )

        return argparser

    argparser = make_argparser()
    args = argparser.parse_args()

    return update_code(args.box2d_tag, args.force)


if __name__ == "__main__":
    try:
        sys.exit(main())
    except subprocess.CalledProcessError as err:
        sys.exit(err.returncode)
    except KeyboardInterrupt:
        sys.exit(1)
