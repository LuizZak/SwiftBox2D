from pycparser import c_ast
from pycparser import c_generator


def identifierFromType(typ: c_ast.TypeDecl) -> str | None:
    inner = typ.type
    if not isinstance(inner, c_ast.IdentifierType):
        return None

    if len(inner.names) != 1:
        return None

    return inner.names[0]


def declarationFromType(typ: c_ast.Decl) -> tuple[str, str] | None:
    """
    Returns a type and identifier from a given c_ast.Decl, in case it matches
    the type of a declaration.
    """
    if isinstance(typ, c_ast.TypeDecl):
        if typ.declname is None:
            return None

        return (typ.declname, cStringFromNode(typ.type))
    if isinstance(typ, c_ast.PtrDecl):
        inner = declarationFromType(typ.type)
        if inner is None:
            return None

        return (inner[0], f"*{inner[1]}")

    raise Exception(f"Unknown declaration type {type(typ)}")

    return None


def cStringFromNode(node: c_ast.Node) -> str:
    return c_generator.CGenerator(True).visit(node)
