from pycparser import c_ast

from utils.data.swift_type import SwiftType


class SwiftTypeMapper:
    """
    A type mapper that converts C types to equivalent or approximate Swift types.
    """

    _simpleTypes: list[tuple[str, str | list[str]]] = [
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

    def mapToSwiftType(self, cDecl: c_ast.Node, context: c_ast.FileAST) -> SwiftType | None:
        if isinstance(cDecl, c_ast.Decl):
            return self.mapToSwiftType(cDecl.type, context)
        elif isinstance(cDecl, c_ast.TypeDecl):
            return self.mapToSwiftType(cDecl.type, context)
        elif isinstance(cDecl, c_ast.PtrDecl):
            inner = self.mapToSwiftType(cDecl.type, context)
            if inner is None:
                return None
            if inner.isEquivalent(SwiftType.void()):
                return SwiftType.typeName("UnsafeMutableRawPointer")
            return SwiftType.generic("UnsafeMutablePointer", [inner])
        elif isinstance(cDecl, c_ast.IdentifierType):
            return self.mapCompoundName(cDecl.names, context)
        elif isinstance(cDecl, c_ast.FuncDecl):
            ret_type = self.mapToSwiftType(cDecl.type, context)

        return None
    
    def mapCompoundName(self, names: list[str], context: c_ast.FileAST) -> SwiftType | None:
        full = " ".join(names)
        for (swiftType, aliases) in self._simpleTypes:
            if full == aliases:
                return SwiftType.typeName(swiftType)
            
            if isinstance(aliases, list):
                for alias in aliases:
                    if full == alias:
                        return SwiftType.typeName(swiftType)
        
        if len(names) == 1:
            return self.expandTypeDef(names[0], context)

        return None
    
    def expandTypeDef(self, typeName: str, context: c_ast.FileAST) -> SwiftType | None:
        for decl in context.ext:
            if isinstance(decl, c_ast.Typedef):
                pass
        
        return SwiftType.typeName(typeName)


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
    void e(g* a);
    """

    parser = pycparser.CParser()
    node: c_ast.FileAST = parser.parse(src, "<stdin>")

    node.show()

    mapper = SwiftTypeMapper()
    for decl in node.ext[-1:]:
        print(mapper.mapToSwiftType(decl, node))
