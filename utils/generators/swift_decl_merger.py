from typing import Iterable
from utils.data.swift_decls import (
    SwiftDecl,
    SwiftExtensionDecl,
    SwiftMemberDecl,
    SwiftMemberVarDecl,
    SwiftMemberFunctionDecl,
)
from pycparser import c_ast

from utils.doccomment.doccomment_block import DoccommentBlock


class SwiftDeclMerger:
    """
    Merges Swift declarations that share a name into combined declarations.
    """

    def merge(self, decls: list[SwiftDecl]) -> list[SwiftDecl]:
        decl_dict: dict[str, SwiftDecl] = dict()

        for decl in decls:
            decl_name = decl.name.to_string()
            existing = decl_dict.get(decl_name)
            if existing is not None:
                if ext_decl := self.try_merge_as_extensions(existing, decl):
                    decl_dict[decl_name] = ext_decl
                    continue

                existing_name = existing.name.to_string()
                existing_original = (
                    existing.original_name
                    if existing.original_name is not None
                    else "<none>"
                )
                decl_original = (
                    decl.original_name if decl.original_name is not None else "<none>"
                )

                raise Exception(
                    f"Found two symbols that share the same name but are of different types or access levels: {existing_name} (type: {type(existing)}) (originally: {existing_original}) and {decl_name} (type: {type(decl)}) (originally: {decl_original})"
                )
            else:
                decl_dict[decl_name] = decl

        return list(decl_dict.values())

    def try_merge_as_extensions(
        self, decl1: SwiftDecl, decl2: SwiftDecl
    ) -> SwiftExtensionDecl | None:
        if not (
            isinstance(decl1, SwiftExtensionDecl)
            and isinstance(decl2, SwiftExtensionDecl)
        ):
            return None

        # Don't merge different access levels
        if decl1.access_level != decl2.access_level:
            return None

        node = self.choose_nodes(decl1.original_node, decl2.original_node)
        members = self.try_merge_members(decl1.members, decl2.members)

        return SwiftExtensionDecl(
            name=decl1.name,
            original_name=decl1.original_name,
            members=members,
            origin=decl1.origin,
            original_node=node,
            c_kind=decl1.c_kind,
            doccomment=decl1.doccomment,
            conformances=list(set(decl1.conformances + decl2.conformances)),
            access_level=decl1.access_level,
        )

    def try_merge_members(
        self, members1: Iterable[SwiftMemberDecl], members2: Iterable[SwiftMemberDecl]
    ) -> list[SwiftMemberDecl]:
        result = list(members1)

        def index_of(member: SwiftMemberDecl) -> int:
            for i, existing in enumerate(result):
                if not isinstance(existing, type(member)):
                    continue
                if existing.name == member.name:
                    return i

            return -1

        for next_member in members2:
            index = index_of(next_member)
            if index == -1:
                result.append(next_member)
                continue

            existing = result[index]
            if isinstance(next_member, SwiftMemberVarDecl) and isinstance(
                existing, SwiftMemberVarDecl
            ):
                result[index] = self.try_merge_member_var_decls(next_member, existing)
            elif isinstance(next_member, SwiftMemberFunctionDecl) and isinstance(
                existing, SwiftMemberFunctionDecl
            ):
                result[index] = self.try_merge_member_func_decls(next_member, existing)

        return result

    def try_merge_member_var_decls(
        self, decl1: SwiftMemberVarDecl, decl2: SwiftMemberVarDecl
    ) -> SwiftMemberVarDecl:
        result = decl1.copy()

        if decl1.name != decl2.name:
            raise Exception(
                f"Attempted to merge two member variable symbols that don't share a name: {decl1.name.to_string()} and {decl2.name.to_string()}"
            )
        if decl1.var_type != decl2.var_type:
            raise Exception(
                f"Attempted to merge two member variable symbols that don't share a type: {decl1.name.to_string()} ({decl1.var_type}) and {decl2.name.to_string()} ({decl2.var_type})"
            )
        if decl1.is_static != decl2.is_static:
            raise Exception(
                f"Found two member variable symbols that don't share the same is_static: {decl1.name.to_string()} ({decl1.is_static}) and {decl2.name.to_string()} ({decl2.is_static})"
            )
        if (
            decl1.initial_value is not None
            and decl2.initial_value is not None
            and decl1.initial_value != decl2.initial_value
        ):
            raise Exception(
                f"Found two member variable symbols that have different initial values defined: {decl1.name.to_string()} ({decl1.initial_value}) and {decl2.name.to_string()} ({decl2.initial_value})"
            )
        if decl2.initial_value is not None:
            result.initial_value = decl2.initial_value
        if decl2.accessor_block is not None:
            if result.accessor_block is not None:
                result.accessor_block += decl2.accessor_block
            else:
                result.accessor_block = decl2.accessor_block

        result.doccomment = self.try_merge_doccomments(decl1, decl2)

        return result

    def try_merge_member_func_decls(
        self, decl1: SwiftMemberFunctionDecl, decl2: SwiftMemberFunctionDecl
    ) -> SwiftMemberFunctionDecl:
        result = decl1.copy()

        if decl1.body != decl2.body:
            if len(decl1.body) == 0:
                result.body = decl2.body
            elif len(decl2.body) != 0:
                raise Exception(
                    f"Found two member function symbols that have different bodies defined: {decl1.name.to_string()} ({decl1.body}) and {decl2.name.to_string()} ({decl2.body})"
                )

        if decl1.parameters != decl2.parameters:
            if len(decl1.parameters) == 0:
                result.parameters = list(decl2.parameters)
            elif len(decl2.parameters) != 0:
                raise Exception(
                    f"Found two member function symbols that have different argument sets defined: {decl1.name.to_string()} ({decl1.parameters}) and {decl2.name.to_string()} ({decl2.parameters})"
                )

        if decl1.return_type != decl2.return_type:
            if decl1.return_type is None:
                result.return_type = decl2.return_type
            elif decl2.return_type is not None:
                raise Exception(
                    f"Found two member function symbols that have different return types defined: {decl1.name.to_string()} ({decl1.return_type}) and {decl2.name.to_string()} ({decl2.return_type})"
                )

        result.doccomment = self.try_merge_doccomments(decl1, decl2)

        return result

    def try_merge_doccomments(
        self,
        v1: SwiftDecl | DoccommentBlock | None,
        v2: SwiftDecl | DoccommentBlock | None,
    ) -> DoccommentBlock | None:
        c1 = v1.doccomment if isinstance(v1, SwiftDecl) else v1
        c2 = v2.doccomment if isinstance(v2, SwiftDecl) else v2

        if c1 is None:
            return c2
        if c2 is None:
            return c1

        if c1.comment_contents == c2.comment_contents:
            return c1

        return c1.copy().with_contents(f"{c1.comment_contents}\n{c2.comment_contents}")

    def choose_nodes(
        self, node1: c_ast.Node | None, node2: c_ast.Node | None
    ) -> c_ast.Node | None:
        if node1 is None:
            return node2
        if node2 is None:
            return node1

        # Choose the source node that has members, if possible
        match (node1, node2):
            case (c_ast.Struct(), c_ast.Struct()):
                if node1.decls is None:
                    return node2
                if node2.decls is None:
                    return node1

        return node1
