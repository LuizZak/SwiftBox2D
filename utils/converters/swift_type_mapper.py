if __name__ == "__main__":
    import sys
    import pathlib

    sys.path.insert(0, str(pathlib.Path(__file__).joinpath("../../../").resolve()))

from dataclasses import dataclass
from pycparser import c_ast

from utils.data.swift_type import (
    OptionalSwiftType,
    SwiftType,
    NominalSwiftType,
    FunctionSwiftType,
)


class SwiftTypeMapper:
    """
    A type mapper that converts C types to equivalent or approximate Swift types.
    """

    _InternalTypeResult = tuple[
        SwiftType,  # Resolved unaliased Swift type.
        SwiftType,  # Resolved Swift type, with aliased typedefs in place.
    ]

    @dataclass()
    class _Flags:
        is_constant: bool = False

        @classmethod
        def from_node(cls, node: c_ast.Node):
            if not isinstance(node, c_ast.Decl):
                return cls()

            return cls(is_constant="const" in node.quals)

    __default_pointer_type = "UnsafeMutablePointer"
    __default_const_pointer_type = "UnsafePointer"
    __void_pointer_type = "UnsafeMutableRawPointer"
    __const_void_pointer_type = "UnsafeRawPointer"

    __simpleTypes: list[tuple[str, str | list[str]]] = [
        ("Void", "void"),
        ("Bool", "_Bool"),
        ("Float", "float"),
        ("Double", "double"),
        ("CChar", ["char", "signed char"]),
        ("CUnsignedChar", ["unsigned char"]),
        ("Int8", ["int8_t"]),
        ("UInt8", ["uint8_t"]),
        ("Int16", ["short", "short int", "signed short int", "short signed int"]),
        ("UInt16", ["unsigned short", "unsigned short int", "short unsigned int"]),
        (
            "Int32",
            [
                "int32_t",
                "intptr_t",
                "int",
                "long",
                "long int",
                "signed int",
                "int signed",
                "signed long",
                "signed long int",
                "long signed int",
                "long int signed",
            ],
        ),
        (
            "UInt32",
            [
                "uint32_t",
                "unsigned int",
                "unsigned long",
                "unsigned long int",
                "long unsigned int",
                "long int unsigned",
            ],
        ),
        (
            "Int64",
            [
                "int64_t",
                "long long",
                "long long int",
                "signed long long",
                "signed long long int",
                "long long signed int",
                "long long int signed",
            ],
        ),
        ("UInt64", ["uint64_t", "unsigned long long", "unsigned long long int"]),
    ]

    __cached_typedefs: dict[str, c_ast.Typedef] | None = None
    __cached_typedef_resolves: dict[str, _InternalTypeResult] | None = None

    def enable_caching(self, ast: c_ast.FileAST):
        """
        Caches information such as typedefs from a given AST to be used as a fast
        lookup for the future type mappings until `reset_cache()` is called.
        When this is set the `context` parameter of `map_to_swift_type()` and
        `unalias_type()` are ignored.
        """
        self.__cached_typedefs = {
            decl.name: decl for decl in ast.ext if isinstance(decl, c_ast.Typedef)
        }
        self.__cached_typedef_resolves = dict()

    def disable_caching(self):
        """Resets the cached typedef lookups back to default."""
        self.__cached_typedefs = None
        self.__cached_typedef_resolves = None

    def map_to_swift_type(
        self, c_decl: c_ast.Node, context: c_ast.FileAST
    ) -> SwiftType | None:
        if mapped := self._map_base(c_decl, context):
            return mapped[0]

        return None

    def unalias_type(self, type_name: str, context: c_ast.FileAST) -> SwiftType | None:
        """
        Returns the fully resolved unaliased type of name `type_name`, if it is a typedef, returns `None` otherwise.
        """
        if expanded := self._expand_type_def(type_name, context):
            return expanded[0]

        return None

    def _map_base(
        self, c_decl: c_ast.Node, context: c_ast.FileAST, flags=_Flags()
    ) -> _InternalTypeResult | None:
        mapped = self._map(c_decl, context)
        if mapped is None:
            return None

        match mapped[0]:
            # Pointer to function typedef maps to the function typedef itself
            case OptionalSwiftType(
                NominalSwiftType(self.__default_pointer_type, [FunctionSwiftType()])
            ):
                return (
                    mapped[1].as_optional_sugar_type().type.as_generic_type()[1][0],
                    mapped[1].as_optional_sugar_type().type.as_generic_type()[1][0],
                )

        return mapped

    def _map(
        self, c_decl: c_ast.Node, context: c_ast.FileAST, flags=_Flags()
    ) -> _InternalTypeResult | None:
        """Maps a C declaration node to an equivalent Swift type, un-aliasing any typedef along the way."""

        if isinstance(c_decl, c_ast.Decl):
            return self._map(c_decl.type, context, self._Flags.from_node(c_decl))
        elif isinstance(c_decl, c_ast.TypeDecl):
            if isinstance(c_decl.type, c_ast.Struct) or isinstance(
                c_decl.type, c_ast.Enum
            ):
                return (
                    SwiftType.type_name(c_decl.declname),
                    SwiftType.type_name(c_decl.declname),
                )

            return self._map(c_decl.type, context)
        elif isinstance(c_decl, c_ast.Typedef):
            if type := self._map(c_decl.type, context):
                return type[0], SwiftType.type_name(c_decl.name)
        elif isinstance(c_decl, c_ast.PtrDecl):
            inner = self._map(c_decl.type, context)
            if inner is None:
                return None
            return self._make_pointer_type(inner[0], inner[1], flags)
        elif isinstance(c_decl, c_ast.IdentifierType):
            return self._map_compound_name(c_decl.names, context)
        elif isinstance(c_decl, c_ast.ArrayDecl):
            # Check if dimensions can be mapped to a constant number
            if not isinstance(c_decl.dim, c_ast.Constant):
                return None

            if (dimension := int(c_decl.dim.value)) <= 0:
                return None

            if (base := self._map(c_decl.type, context, flags)) is None:
                return None

            return (
                SwiftType.tuple([base[0]] * dimension),
                SwiftType.tuple([base[1]] * dimension)
            )
        elif isinstance(c_decl, c_ast.FuncDecl):
            ret_type = self._map_base(c_decl.type, context)
            if ret_type is None:
                return None

            if c_decl.args.params is None:
                return (
                    SwiftType.function([], ret_type[0]),
                    SwiftType.function([], ret_type[0]),
                )

            params = []
            for p in c_decl.args.params:
                if typ := self._map_base(p, context=context):
                    params.append(typ[0])
                else:
                    return None

            return (
                SwiftType.function(params, ret_type[0]),
                SwiftType.function(params, ret_type[0]),
            )

        return None

    def _map_compound_name(
        self, names: list[str], context: c_ast.FileAST
    ) -> _InternalTypeResult | None:
        full = " ".join(names)
        for swift_type, aliases in self.__simpleTypes:
            if isinstance(aliases, str):
                if full == aliases:
                    return (
                        SwiftType.type_name(swift_type),
                        SwiftType.type_name(swift_type),
                    )
                continue

            for alias in aliases:
                if full == alias:
                    return (
                        SwiftType.type_name(swift_type),
                        SwiftType.type_name(swift_type),
                    )

        if len(names) == 1:
            return self._expand_type_def(names[0], context)

        return None

    def _make_pointer_type(
        self, pointee: SwiftType, unaliased: SwiftType, flags: _Flags
    ) -> _InternalTypeResult:
        # void* should map to UnsafeMutableRawPointer/UnsafeRawPointer
        if pointee.is_equivalent(SwiftType.void_type()):
            pointer_type = (
                self.__const_void_pointer_type
                if flags.is_constant
                else self.__void_pointer_type
            )
            return (
                SwiftType.type_name(pointer_type).wrap_optional(),
                SwiftType.type_name(pointer_type).wrap_optional(),
            )

        pointer_type = (
            self.__default_const_pointer_type
            if flags.is_constant
            else self.__default_pointer_type
        )
        return (
            SwiftType.generic(pointer_type, [pointee]).wrap_optional(),
            SwiftType.generic(pointer_type, [unaliased]).wrap_optional(),
        )

    def _expand_type_def(
        self, type_name: str, context: c_ast.FileAST
    ) -> _InternalTypeResult | None:
        if self.__cached_typedef_resolves is not None:
            if cached := self.__cached_typedef_resolves.get(type_name):
                return cached

            if result := self.__expand_type_def(type_name, context):
                self.__cached_typedef_resolves[type_name] = result
                return result
            else:
                return None

        return self.__expand_type_def(type_name, context)

    def __expand_type_def(
        self, type_name: str, context: c_ast.FileAST
    ) -> _InternalTypeResult | None:
        if self.__cached_typedefs is not None:
            if not (decl := self.__cached_typedefs.get(type_name)):
                return None

            if typ := self._map(decl.type, context):
                return (
                    typ[0],
                    SwiftType.type_name(type_name),
                )
            else:
                return None

        for decl in context.ext:
            if not isinstance(decl, c_ast.Typedef):
                continue
            if decl.name != type_name:
                continue

            if type := self._map(decl.type, context):
                return (
                    type[0],
                    SwiftType.type_name(type_name),
                )

            return None

        return (
            SwiftType.type_name(type_name),
            SwiftType.type_name(type_name),
        )


if __name__ == "__main__":
    import pycparser

    def __test():
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
        const int *k;
        long unsigned int l;
        short signed int m;
        int n[10];
        long *p[5];
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

    __test()
