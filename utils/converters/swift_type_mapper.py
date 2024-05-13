if __name__ == "__main__":
    import sys
    import pathlib
    sys.path.insert(0, str(pathlib.Path(__file__).joinpath("../../../").resolve()))

from dataclasses import dataclass
from pycparser import (c_ast, c_generator)

from utils.data.swift_type import (
    OptionalSwiftType,
    SwiftType,
    NominalSwiftType,
    FunctionSwiftType
)


class SwiftTypeMapper:
    """
    A type mapper that converts C types to equivalent or approximate Swift types.
    """

    @dataclass
    class __InternalTypeResult:
        name: str
        "Original C name, or raw C type string."
        swift_type: SwiftType
        "Resolved unaliased Swift type."
        swift_type_aliased: SwiftType
        "Resolved Swift type, with aliased typedefs in place."

    __default_pointer_type = "UnsafeMutablePointer"
    __simpleTypes: list[tuple[str, str | list[str]]] = [
        ("Void", "void"),
        ("Bool", "_Bool"),
        ("Float", "float"),
        ("Double", "double"),
        ("CChar", ["char", "signed char"]),
        ("CUnsignedChar", ["unsigned char"]),
        ("Int8", ["int8_t"]),
        ("UInt8", ["uint8_t"]),
        ("Int32", ["int32_t", "intptr_t", "int", "long", "long int", "signed int", "signed long", "signed long int"]),
        ("UInt32", ["uint32_t", "unsigned int"]),
        ("Int64", ["int64_t", "long long", "long long int", "signed long long", "signed long long int"]),
        ("UInt64", ["uint64_t", "unsigned long long", "unsigned long long int"]),
    ]

    def map_to_swift_type(self, cDecl: c_ast.Node, context: c_ast.FileAST) -> SwiftType | None:
        if mapped := self.__map_base(cDecl, context):
            return mapped.swift_type
        
        return None
    
    def unalias_type(self, type_name: str, context: c_ast.FileAST) -> SwiftType | None:
        "Returns the fully resolved unaliased type of name `type_name`, if it is a typedef, returns `None` otherwise."
        if expanded := self.__expand_type_def(type_name, context):
            return expanded.swift_type
        
        return None

    def __map_base(self, cDecl: c_ast.Node, context: c_ast.FileAST) -> __InternalTypeResult | None:
        mapped = self.__map(cDecl, context)
        if mapped is None:
            return None
        
        # Pointer to function typedef maps to the function typedef itself
        match mapped.swift_type:
            case OptionalSwiftType(NominalSwiftType(self.__default_pointer_type, [FunctionSwiftType()])):
                return self.__InternalTypeResult(
                    mapped.name,
                    mapped.swift_type_aliased.as_optional_sugar_type().type.as_generic_type()[1][0],
                    mapped.swift_type_aliased.as_optional_sugar_type().type.as_generic_type()[1][0]
                )
        
        return mapped

    def __map(self, cDecl: c_ast.Node, context: c_ast.FileAST) -> __InternalTypeResult | None:
        "Maps a C declaration node to an equivalent Swift type, un-aliasing any typedef along the way."

        if isinstance(cDecl, c_ast.Decl):
            return self.__map(cDecl.type, context)
        elif isinstance(cDecl, c_ast.TypeDecl):
            if isinstance(cDecl.type, c_ast.Struct) or isinstance(cDecl.type, c_ast.Enum):
                return self.__InternalTypeResult(
                    self.__c_string(cDecl),
                    SwiftType.typeName(cDecl.declname),
                    SwiftType.typeName(cDecl.declname)
                )
            
            return self.__map(cDecl.type, context)
        elif isinstance(cDecl, c_ast.Typedef):
            if type := self.__map(cDecl.type, context):
                return self.__InternalTypeResult(
                    self.__c_string(cDecl),
                    type.swift_type,
                    SwiftType.typeName(cDecl.name)
                )
        elif isinstance(cDecl, c_ast.PtrDecl):
            inner = self.__map(cDecl.type, context)
            if inner is None:
                return None
            # void* should map to UnsafeMutableRawPointer
            if inner.swift_type.isEquivalent(SwiftType.void()):
                return self.__InternalTypeResult(
                    self.__c_string(cDecl),
                    SwiftType.typeName("UnsafeMutableRawPointer").wrap_optional(),
                    SwiftType.typeName("UnsafeMutableRawPointer").wrap_optional()
                )
            return self.__InternalTypeResult(
                self.__c_string(cDecl),
                SwiftType.generic(self.__default_pointer_type, [inner.swift_type]).wrap_optional(),
                SwiftType.generic(self.__default_pointer_type, [inner.swift_type_aliased]).wrap_optional(),
            )
        elif isinstance(cDecl, c_ast.IdentifierType):
            return self.__map_compound_name(cDecl.names, context)
        elif isinstance(cDecl, c_ast.FuncDecl):
            ret_type = self.__map_base(cDecl.type, context)
            if ret_type is None:
                return None
            
            if cDecl.args.params is None:
                return self.__InternalTypeResult(
                    self.__c_string(cDecl),
                    SwiftType.function([], ret_type.swift_type),
                    SwiftType.function([], ret_type.swift_type),
                )

            params = []
            for p in cDecl.args.params:
                if type := self.__map_base(p, context=context):
                    params.append(type.swift_type)
                else:
                    return None
            
            return self.__InternalTypeResult(
                self.__c_string(cDecl),
                SwiftType.function(params, ret_type.swift_type),
                SwiftType.function(params, ret_type.swift_type),
            )

        return None
    
    def __map_compound_name(self, names: list[str], context: c_ast.FileAST) -> __InternalTypeResult | None:
        full = " ".join(names)
        for (swiftType, aliases) in self.__simpleTypes:
            if isinstance(aliases, str):
                if full == aliases:
                    return self.__InternalTypeResult(
                        full,
                        SwiftType.typeName(swiftType),
                        SwiftType.typeName(swiftType),
                    )
                continue
            
            for alias in aliases:
                if full == alias:
                    return self.__InternalTypeResult(
                        full,
                        SwiftType.typeName(swiftType),
                        SwiftType.typeName(swiftType),
                    )
        
        if len(names) == 1:
            return self.__expand_type_def(names[0], context)

        return None
    
    def __expand_type_def(self, typeName: str, context: c_ast.FileAST) -> __InternalTypeResult | None:
        for decl in context.ext:
            if not isinstance(decl, c_ast.Typedef):
                continue
            if decl.name != typeName:
                continue

            if type := self.__map(decl.type, context):
                return self.__InternalTypeResult(
                    type.name,
                    type.swift_type,
                    SwiftType.typeName(typeName),
                )
            
            return None
        
        return self.__InternalTypeResult(
            typeName,
            SwiftType.typeName(typeName),
            SwiftType.typeName(typeName),
        )
    
    def __c_string(self, node: c_ast.Node):
        return c_generator.CGenerator(True).visit(node)


if __name__ == "__main__":
    import pycparser

    src = """
    int *a;
    void *b;
    unsigned int c;
    long long d;
    signed long long e;
    unsigned long long f;
    typedef void* g(unsigned int a, int b);
    void h(g* a);
    typedef struct { int b; } i;
    void j(i a);
    """

    parser = pycparser.CParser()
    node: c_ast.FileAST = parser.parse(src, "<stdin>")

    node.show()

    mapper = SwiftTypeMapper()
    for decl in node.ext:
        if typ := mapper.map_to_swift_type(decl, node):
            print(typ.to_string())
        else:
            print(None)
