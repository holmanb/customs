#!/usr/bin/env python3

"""
A static code analysis tool capable of identifying module import side-effects.
"""

import argparse
import ast
import os
import sys
from pathlib import Path
from typing import NamedTuple, List


class Violation(NamedTuple):
    """
    Every rule violation contains a node that breaks the rule,
    and a message that will be shown to the user.
    """

    node: ast.AST
    message: str


class Checker(ast.NodeVisitor):
    """
    A Checker is a Visitor that defines a lint rule, and stores all the
    nodes that violate that lint rule.
    """

    def __init__(self, issue_code: str) -> None:
        self.issue_code = issue_code
        self.violations: set[Violation] = set()


# potential other tests:
#          -- use 'orelse' because else is a keyword in target languages
#          | For(expr target, expr iter, stmt* body, stmt* orelse, string? type_comment)
#          | AsyncFor(expr target, expr iter, stmt* body, stmt* orelse, string? type_comment)
#          | While(expr test, stmt* body, stmt* orelse)
#          | If(expr test, stmt* body, stmt* orelse)
#          | With(withitem* items, stmt* body, string? type_comment)
#          | AsyncWith(withitem* items, stmt* body, string? type_comment)
#
#          | Match(expr subject, match_case* cases)


class CallImportChecker(Checker):
    """Check for `Call`s executed during import time."""

    def __init__(self, issue_code: str) -> None:
        super().__init__(issue_code)
        # TODO: make this configurable
        self.exceptions = ["getLogger"]

    def visit_Assign(self, node: ast.Assign):
        """check for Call in variable assignment"""
        # not the start of a line
        if 0 != node.col_offset:
            return

        # not a type call
        if not isinstance(node.value, ast.Call):
            return

        # skip anything in a hardcoded list of exceptions
        if isinstance(node.value.func, ast.Attribute):
            if node.value.func.attr in self.exceptions:
                return
        if isinstance(node.value.func, ast.Name):
            if node.value.func.id in self.exceptions:
                return

        self.violations.add(Violation(node, "Import invoked a Call"))

    def visit_Call(self, node: ast.Call):
        """check for a Call"""
        # not the start of a line
        if 0 != node.col_offset:
            return

        # skip anything in a hardcoded list of exceptions
        if isinstance(node.func, ast.Attribute) and node.func.attr in self.exceptions:
            return
        if (
            isinstance(node.func, (ast.Name, ast.Assign))
            and node.func.id in self.exceptions
        ):
            return
        self.violations.add(Violation(node, "Import invoked a Call"))


class Linter:
    """Holds all list rules, and runs them against a source file."""

    def __init__(self) -> None:
        self.checkers: set[Checker] = set()

    @classmethod
    def print_violations(
        cls, checker: Checker, file_name: str, source_code: str, verbose
    ):
        """Prints all violations collected by a checker."""
        for node, message in checker.violations:
            code = f"{ast.get_source_segment(source_code, node)}" if verbose else ""
            message = (
                f"{file_name}:{node.lineno}:{node.col_offset}: "
                f"{checker.issue_code}: {message}"
            )
            print(cls.format_code(message, code))

        # all violations have been reported, clear for a fresh slate with the next file
        checker.violations = set()

    @staticmethod
    def format_code(message: str, code: str) -> str:
        """Append code after standard message."""
        if not code:
            return message

        barrier = " | "
        left_pad = " " * len(message) + barrier
        interleave = [message + barrier]
        if "\n" not in code:
            return message + barrier + code
        for line in code.split("\n"):
            if not line:
                continue
            interleave.append(line + "\n")
            interleave.append(left_pad)
        return "".join(interleave)

    def run(self, file_name: str, source_code: str, verbose: bool = False) -> None:
        """Runs all lints on a source file."""
        tree = ast.parse(source_code)
        for checker in self.checkers:
            checker.visit(tree)
            self.print_violations(checker, file_name, source_code, verbose)


def lint(files: List[str], verbose: bool = False):
    """Create a Linter, add checkers, then run against the files."""
    linted_files = 0
    linter = Linter()
    linter.checkers.add(CallImportChecker(issue_code="W001"))
    for source_path in files:
        if not Path(source_path).is_file():
            if verbose:
                print(f"ignoring file: {source_path}", file=sys.stderr)
            continue
        with open(source_path) as source_file:
            file_name = os.path.basename(source_path)
            source_code = source_file.read()
            linter.run(file_name, source_code, verbose)
            linted_files += 1
    print(f"Analyzed {linted_files} files\n", file=sys.stderr, flush=True)


def parser():
    """Define an argument parser"""
    p = argparse.ArgumentParser(
        prog="customs",
        description=(
            "A static code analysis tool capable of identifing module "
            "import side-effects."
        ),
    )
    p.add_argument("--verbose", action="store_true", help="Include source code.")
    p.add_argument("files", nargs="*", help="Files to analyze.")
    return p.parse_args()


def main() -> None:
    """main function"""
    args = parser()
    lint(args.files, args.verbose)


if __name__ == "__main__":
    main()
