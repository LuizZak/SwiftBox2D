from dataclasses import dataclass, field
from enum import Enum
from typing import List
from pathlib import Path

from pycparser import c_ast
from utils.text.syntax_stream import SyntaxStream
from utils.converters.backticked_term import backticked_term
from utils.data.c_decl_kind import CDeclKind
from utils.data.compound_symbol_name import CompoundSymbolName
from utils.data.swift_decl_visit_result import SwiftDeclVisitResult
from utils.data.swift_decl_visitor import SwiftDeclVisitor
from utils.data.swift_type import SwiftType
from utils.doccomment.doccomment_block import DoccommentBlock


class SwiftAccessLevel(Enum):
    """
    Represents an access level for a Swift declaration.
    """

    PRIVATE = "private"
    FILEPRIVATE = "fileprivate"
    INTERNAL = "internal"
    PUBLIC = "public"
    OPEN = "open"

    @classmethod
    def resolve(cls, access: "SwiftAccessLevel | None"):
        """
        Resolves an optional access level by returning `SwiftAccessLevel.INTERNAL`
        if `access is None`, and returning `access` itself, otherwise, mimicking
        how Swift itself selects access levels for symbols that don't specify them.
        """
        return access if access is not None else SwiftAccessLevel.INTERNAL

    def write(self, stream: SyntaxStream):
        stream.write(self.name.lower())

    def is_more_visible(self, other: "SwiftAccessLevel"):
        """
        Returns `True` if `self` represents a higher visibility than `other`.
        Returns `False` if `self` is open or public, since these are the highest
        visibility levels in Swift.
        """
        a = SwiftAccessLevel
        match (self, other):
            # private
            case (a.PRIVATE, _):
                return False
            # fileprivate > private
            case (a.FILEPRIVATE, a.PRIVATE):
                return True
            case (a.FILEPRIVATE, _):
                return False
            # internal > fileprivate > private
            case (a.INTERNAL, a.PRIVATE) | (a.INTERNAL, a.FILEPRIVATE):
                return True
            case (a.INTERNAL, _):
                return False
            # public > internal > fileprivate > private
            case (
                (a.PUBLIC, a.PRIVATE)
                | (a.PUBLIC, a.FILEPRIVATE)
                | (a.PUBLIC, a.INTERNAL)
            ):
                return True
            case (a.PUBLIC, _):
                return False
            # open > internal > fileprivate > private
            case (a.OPEN, a.PRIVATE) | (a.OPEN, a.FILEPRIVATE) | (a.OPEN, a.INTERNAL):
                return True
            case (a.OPEN, _):
                return False

    def less_visible(self, other: "SwiftAccessLevel"):
        """Returns the less visible access level between `self` and `other`."""
        if self.is_more_visible(other):
            return other
        return self

    @classmethod
    def resolve_member_outside(
        cls,
        type_access: "SwiftAccessLevel | None",
        member_access: "SwiftAccessLevel | None",
    ) -> "SwiftAccessLevel":
        """
        Resolves access level of a member of a type outside of that type using
        Swift-like resolution rules according to the given pseudo-code:

        ```
        match (type, member):
            (None, None):
                Internal
            (None, not None):
                member
            (not None, None):
                type
            (not None, not None):
                least visible between type and member
        ```
        """

        match (type_access, member_access):
            case (None, None):
                return cls.INTERNAL
            case (type, None) if type is not None:
                return type
            case (None, member) if member is not None:
                return member
            case (type, member) if type is not None and member is not None:
                return cls.less_visible(type, member)

        return cls.INTERNAL


@dataclass(slots=True)
class SourceLocation(object):
    file: Path
    line: int
    column: int | None


@dataclass
class SwiftDecl(object):
    name: CompoundSymbolName
    original_name: str | None
    origin: SourceLocation | None

    original_node: c_ast.Node | None
    """
    Original node that produced this declaration. Is None if this declaration
    is synthesized instead.
    """

    c_kind: CDeclKind

    doccomment: DoccommentBlock | None
    "A block of doc comments associated with this element."

    def write(self, stream: SyntaxStream):
        if self.doccomment is None:
            return

        comment_str = self.doccomment.comment_contents

        for line in comment_str.splitlines():
            stream.line(f"/// {line}")

    def copy(self):
        raise NotImplementedError("Must be implemented by subclasses.")

    def walk(self, visitor: SwiftDeclVisitor):
        """
        Starts walking with a generic declaration walker within this declaration
        with a given visitor.
        """
        walker = SwiftDeclWalker(visitor)
        walker.walk_decl(self)

    def accept(self, visitor: SwiftDeclVisitor) -> SwiftDeclVisitResult:
        raise NotImplementedError("Must be implemented by subclasses.")

    def accept_post(self, visitor: SwiftDeclVisitor):
        raise NotImplementedError("Must be implemented by subclasses.")

    def children(self) -> list["SwiftDecl"]:
        raise NotImplementedError("Must be implemented by subclasses.")


@dataclass
class SwiftMemberDecl(SwiftDecl):
    """
    A Swift member declaration base class.
    """

    is_static: bool = False
    "Whether this is a static member."

    access_level: SwiftAccessLevel | None = None

    def write(self, stream: SyntaxStream):
        super().write(stream)

        stream.pre_line()

        if self.access_level is not None:
            self.access_level.write(stream)
            stream.write(" ")


@dataclass
class SwiftMemberVarDecl(SwiftMemberDecl):
    """
    A Swift variable member declaration.
    """

    var_type: SwiftType | None = None
    initial_value: str | None = None
    accessor_block: list[str] | None = None

    def write(self, stream: SyntaxStream):
        super().write(stream)

        if self.is_static:
            stream.write("static ")

        # Variables with accessors must use "var" keyword
        if self.accessor_block is None or len(self.accessor_block) == 0:
            stream.write(f"let {backticked_term(self.name.to_string())}")
        else:
            stream.write(f"var {backticked_term(self.name.to_string())}")

        if self.var_type is not None:
            stream.write(f": {self.var_type.to_string()}")

        if self.initial_value is not None:
            stream.write(f" = {self.initial_value}")

        if self.accessor_block is not None and len(self.accessor_block) > 0:
            with stream.inline_block(" {"):
                for line in self.accessor_block:
                    stream.line(line)
        else:
            stream.write_then_line()

    def copy(self):
        return SwiftMemberVarDecl(
            name=self.name.copy(),
            original_name=self.original_name,
            original_node=self.original_node,
            origin=self.origin,
            c_kind=self.c_kind,
            doccomment=self.doccomment,
            is_static=self.is_static,
            var_type=self.var_type,
            initial_value=self.initial_value,
            accessor_block=self.accessor_block,
            access_level=self.access_level,
        )

    def accept(self, visitor: SwiftDeclVisitor) -> SwiftDeclVisitResult:
        return visitor.visit(self)

    def accept_post(self, visitor: SwiftDeclVisitor):
        return visitor.post_visit(self)

    def children(self) -> list["SwiftDecl"]:
        return list()


@dataclass
class SwiftMemberFunctionDecl(SwiftMemberDecl):
    """
    A Swift function member declaration.
    """

    @dataclass
    class ParameterType:
        label: str | None
        name: str
        decorations: str | None
        type: SwiftType

        def copy(self):
            return SwiftMemberFunctionDecl.ParameterType(
                self.label, self.name, self.decorations, self.type
            )

    parameters: list[ParameterType] = field(default_factory=lambda: [])
    "List of function parameters."

    return_type: SwiftType | None = None
    "Return type of function. None produces no return type (implicit Void)"

    body: list[str] = field(default_factory=lambda: [])
    "A function body to emit."

    def write(self, stream: SyntaxStream):
        super().write(stream)

        if self.is_static:
            stream.write("static ")

        # func <name>
        stream.write("func ")
        stream.write(backticked_term(self.name.to_string()))

        # (<argument list>)
        def arg_str(arg: SwiftMemberFunctionDecl.ParameterType) -> str:
            result = ""
            if arg.label is not None:
                result += f"{arg.label} "
            else:
                result += "_ "
            result += f"{arg.name}: "
            if arg.decorations is not None:
                result += f"{arg.decorations} "
            result += arg.type.to_string()
            return result

        stream.write("(")
        stream.write(", ".join(map(arg_str, self.parameters)))
        stream.write(") ")

        if self.return_type is not None and not SwiftType.is_equivalent(
            self.return_type, SwiftType.void_type()
        ):
            stream.write(f"-> {self.return_type.to_string()} ")

        self.write_body(stream)

    def write_body(self, stream: SyntaxStream):
        if len(self.body) == 0:
            stream.write_then_line("{ }")
            return

        with stream.inline_block("{"):
            for line in self.body:
                stream.line(line)

    def copy(self):
        return SwiftMemberFunctionDecl(
            name=self.name.copy(),
            original_name=self.original_name,
            original_node=self.original_node,
            origin=self.origin,
            c_kind=self.c_kind,
            doccomment=self.doccomment,
            parameters=[p.copy() for p in self.parameters],
            return_type=self.return_type,
            body=list(self.body),
            is_static=self.is_static,
            access_level=self.access_level,
        )

    def accept(self, visitor: SwiftDeclVisitor) -> SwiftDeclVisitResult:
        return visitor.visit(self)

    def accept_post(self, visitor: SwiftDeclVisitor):
        return visitor.post_visit(self)

    def children(self) -> list["SwiftDecl"]:
        return list()


@dataclass
class SwiftTypealiasDecl(SwiftDecl):
    access_level: SwiftAccessLevel

    def write(self, stream: SyntaxStream):
        super().write(stream)

        self.access_level.write(stream)
        stream.line(f" typealias {self.name.to_string()} = {self.original_name}")

    def copy(self):
        return SwiftTypealiasDecl(
            name=self.name,
            original_name=self.original_name,
            origin=self.origin,
            original_node=self.original_node,
            c_kind=self.c_kind,
            doccomment=self.doccomment,
            access_level=self.access_level,
        )

    def accept(self, visitor: SwiftDeclVisitor) -> SwiftDeclVisitResult:
        return visitor.visit(self)

    def accept_post(self, visitor: SwiftDeclVisitor):
        return visitor.post_visit(self)

    def children(self) -> list["SwiftDecl"]:
        return []


@dataclass
class SwiftExtensionDecl(SwiftDecl):
    access_level: SwiftAccessLevel
    members: List[SwiftMemberDecl]
    conformances: list[str]

    def conformances_string(self):
        conformances = sorted(self.conformances)
        conformances = [f"@retroactive {c}" for c in conformances]
        return ", ".join(conformances)

    def write(self, stream: SyntaxStream):
        super().write(stream)

        name = self.name.to_string()

        # Emit conformances, with no access control specifier so the code compiles
        # properly
        if len(self.conformances) > 0:
            conformance_str = self.conformances_string()

            stream.line(f"extension {name}: {conformance_str} {{ }}")
            stream.line()

        # Only emit members extension if members are present
        if len(self.members) > 0:
            self.access_level.write(stream)
            member_decl = f" extension {name}"

            if len(self.members) == 0:
                stream.line(member_decl + " { }")
                return

            with stream.block(member_decl + " {"):
                for i, member in enumerate(self.members):
                    if i > 0:
                        stream.line()

                    member.write(stream)

    def copy(self):
        return SwiftExtensionDecl(
            name=self.name.copy(),
            original_name=self.original_name,
            origin=self.origin,
            original_node=self.original_node,
            c_kind=self.c_kind,
            doccomment=self.doccomment,
            members=list(m.copy() for m in self.members),
            conformances=self.conformances,
            access_level=self.access_level,
        )

    def accept(self, visitor: SwiftDeclVisitor) -> SwiftDeclVisitResult:
        return visitor.visit(self)

    def accept_post(self, visitor: SwiftDeclVisitor):
        return visitor.post_visit(self)

    def children(self) -> list["SwiftDecl"]:
        return list(self.members)

    def is_empty(self) -> bool:
        """
        Returns True if this extension declaration is empty (has no members or
        conformances declared)
        """
        return len(self.members) == 0 and len(self.conformances) == 0


class SwiftDeclWalker:
    def __init__(self, visitor: SwiftDeclVisitor):
        self.visitor = visitor

    def walk_decl(self, decl: SwiftDecl):
        result = decl.accept(self.visitor)

        if result == SwiftDeclVisitResult.VISIT_CHILDREN:
            for child in decl.children():
                self.walk_decl(child)

        decl.accept_post(self.visitor)
