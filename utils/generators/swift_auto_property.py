from typing import Mapping
from utils.converters.swift_type_mapper import SwiftTypeMapper
from utils.data.swift_decls import SwiftDecl, SwiftExtensionDecl, SwiftMemberDecl, SwiftMemberFunctionDecl, SwiftMemberVarDecl
from utils.doccomment.doccomment_block import DoccommentBlock


class SwiftAutoProperty:
    """
    Merges Swift method declarations that form getter/setter patterns into property declarations.

    Should be done after all declarations have been named and merged.
    """
    def __init__(self, type_mapper: SwiftTypeMapper | None = None):
        if type_mapper is None:
            self.type_mapper = SwiftTypeMapper()
        else:
            self.type_mapper = type_mapper
    
    def convert(self, swift_decls: list[SwiftDecl]) -> list[SwiftDecl]:
        result: list[SwiftDecl] = []
        for decl in swift_decls:
            if isinstance(decl, SwiftExtensionDecl):
                result.append(self.navigate(decl.copy()))
            else:
                result.append(decl)
            
        return result

    def navigate(self, swift_ext: SwiftExtensionDecl) -> SwiftExtensionDecl:
        getters = [
            (f, f.name.to_string()[3:]) for f in swift_ext.members if isinstance(f, SwiftMemberFunctionDecl) and f.name.startswith('get')
        ]
        setters = [
            (f, f.name.to_string()[3:]) for f in swift_ext.members if isinstance(f, SwiftMemberFunctionDecl) and f.name.startswith('set')
        ]

        grouped: dict[str, list[SwiftMemberFunctionDecl]] = dict()
        for (getter, name) in getters:
            if name in grouped:
                grouped[name].append(getter)
            else:
                grouped[name] = [getter]
        for (setter, name) in setters:
            if name in grouped:
                grouped[name].append(setter)
            else:
                grouped[name] = [setter]
        
        for (_, values) in grouped.items():
            if len(values) != 2:
                continue
            
            (getter, setter) = values
            if getter is None and setter is None:
                continue
            if setter is None:
                continue
            if len(setter.parameters) != 1:
                continue
            if getter.return_type != setter.parameters[0].type:
                continue
            if getter.is_static != setter.is_static:
                continue
            if getter.access_level != setter.access_level:
                continue

            new_name = (
                getter.name
                    .removing_prefixes(['get'])
                    .camel_cased()
            )

            accessor_block: list[str] = []
            accessor_block.append("get {")
            for line in getter.body:
                accessor_block.append(f"    {line}")
            accessor_block.append("}")
            accessor_block.append(f"set({setter.parameters[0].name}) {{")
            for line in setter.body:
                accessor_block.append(f"    {line}")
            accessor_block.append("}")

            synthesized_var = SwiftMemberVarDecl(
                name=new_name,
                original_name=getter.original_name,
                origin=getter.origin,
                original_node=getter.original_node,
                c_kind=getter.c_kind,
                doccomment=DoccommentBlock.merge(getter.doccomment, setter.doccomment),
                is_static=getter.is_static,
                access_level=getter.access_level,
                var_type=getter.return_type,
                accessor_block=accessor_block
            )

            self.remove_member(getter, swift_ext)
            self.remove_member(setter, swift_ext)

            self.add_member(synthesized_var, swift_ext)

        return swift_ext

    def remove_member(self, decl: SwiftMemberDecl, ext: SwiftExtensionDecl):
        ext.members.remove(decl)
    
    def add_member(self, decl: SwiftMemberDecl, ext: SwiftExtensionDecl):
        ext.members.append(decl)
