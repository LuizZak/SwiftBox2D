from dataclasses import dataclass
from typing import Iterable
from utils.converters.syntax_stream import SyntaxStream
import io

@dataclass(slots=True)
class SwiftType:
    "Base class for Swift types."

    # Type factories

    @classmethod
    def typeName(cls, name: str) -> "NominalSwiftType":
        "Creates a nominal Swift type, e.g. `Int`."
        return NominalSwiftType(name)
    
    @classmethod
    def generic(cls, name: str, params: Iterable["SwiftType | str"]) -> "NominalSwiftType":
        "Creates a generic Swift type, e.g. `MyType<Int>`."
        return NominalSwiftType(name, cls._processTypes(params))
    
    @classmethod
    def optional(cls, type: "SwiftType | str") -> "OptionalSwiftType":
        "Creates an Optional sugar Swift type, e.g. `Int?`"
        return OptionalSwiftType(cls._processType(type))
    
    @classmethod
    def implicitly_unwrapped_optional(cls, type: "SwiftType | str") -> "ImplicitlyUnwrappedOptionalSwiftType":
        "Creates an implicitly-unwrapped Optional sugar Swift type, e.g. `Int!`"
        return ImplicitlyUnwrappedOptionalSwiftType(cls._processType(type))
    
    @classmethod
    def array(cls, type: "SwiftType | str") -> "ArraySwiftType":
        "Creates an Array sugar Swift type, e.g. `[Int]`."
        return ArraySwiftType(cls._processType(type))
    
    @classmethod
    def dictionary(cls, key: "SwiftType | str", value: "SwiftType | str") -> "DictionarySwiftType":
        "Creates a Dictionary sugar Swift type, e.g. `[Int: String]`."
        return DictionarySwiftType(cls._processType(key), cls._processType(value))
    
    @classmethod
    def function(cls, parameters: Iterable["SwiftType | str"], returnType: "SwiftType | str") -> "FunctionSwiftType":
        "Creates a Function Swift type, e.g. `(Int) -> String`."
        return FunctionSwiftType(cls._processTypes(parameters), cls._processType(returnType))
    
    @classmethod
    def void(cls) -> "TupleSwiftType":
        "Creates the Void Swift type, i.e. `()`."
        return TupleSwiftType([])
    
    @classmethod
    def tuple(cls, types: Iterable["SwiftType | str"]) -> "TupleSwiftType":
        "Creates a tuple Swift type, e.g. `(Int, String)`."
        return TupleSwiftType(cls._processTypes(types))
    
    @classmethod
    def protocolComposition(cls, components: Iterable["NominalSwiftType | NestedSwiftType"]) -> "ProtocolCompositionSwiftType":
        "Creates a protocol composition Swift type, e.g. `Protocol1 & Protocol2`."
        return ProtocolCompositionSwiftType(components)
    
    @classmethod
    def _processType(cls, type: "SwiftType | str") -> "SwiftType":
        if isinstance(type, SwiftType):
            return type

        return NominalSwiftType(type)
    
    @classmethod
    def _processTypes(cls, types: Iterable["SwiftType | str"]) -> list["SwiftType"]:
        return [cls._processType(type) for type in types]

    # Methods

    def is_function_type(self):
        "Returns `True` if `self` describes a Function type."
        return isinstance(self, FunctionSwiftType)
    
    def is_typename_type(self):
        "Returns `True` if `self` describes a Nominal type."
        return isinstance(self, NominalSwiftType)
    
    def is_nested_type(self):
        "Returns `True` if `self` describes a Nested Nominal type."
        return isinstance(self, NestedSwiftType)
    
    def is_generic_type(self):
        "Returns `True` if `self` describes a Nominal type with generic arguments."
        if isinstance(self, NominalSwiftType):
            return self.genericParameters is not None
        return False
    
    def is_protocol_composition_type(self):
        "Returns `True` if `self` describes a Protocol Composition type."
        return isinstance(self, ProtocolCompositionSwiftType)
    
    def is_tuple_type(self):
        "Returns `True` if `self` describes a Tuple type."
        return isinstance(self, TupleSwiftType)
    
    def is_optional_sugar_type(self):
        "Returns `True` if `self` describes a sugared `Optional<T>` type (i.e. `T?`)."
        return isinstance(self, OptionalSwiftType)
    
    def is_implicitly_unwrapped_optional_sugar_type(self):
        "Returns `True` if `self` describes a sugared implicitly-unwrapped `Optional<T>` type (i.e. `T!`)."
        return isinstance(self, ImplicitlyUnwrappedOptionalSwiftType)
    
    def is_array_sugar_type(self):
        "Returns `True` if `self` describes a sugared `Array<T>` type (i.e. `[T]`)."
        return isinstance(self, ArraySwiftType)
    
    def is_dictionary_sugar_type(self):
        "Returns `True` if `self` describes a sugared `Dictionary<Key, Value>` type (i.e. `[Key: Value]`)."
        return isinstance(self, DictionarySwiftType)
    
    #

    def as_function_type(self):
        "Returns type-cast `self` if `self` describes a Function type, otherwise returns `None`."
        return self if isinstance(self, FunctionSwiftType) else None
    
    def as_typename_type(self):
        "Returns type-cast `self` if `self` describes a Nominal type, otherwise returns `None`."
        return self if isinstance(self, NominalSwiftType) else None
    
    def as_nested_type(self):
        "Returns type-cast `self` if `self` describes a Nested Nominal type, otherwise returns `None`."
        return self if isinstance(self, NestedSwiftType) else None
    
    def as_generic_type(self):
        "Returns type-cast `self` and a list of generic arguments if `self` describes a Nominal type with generic arguments, otherwise returns `None`."
        if isinstance(self, NominalSwiftType) and self.genericParameters is not None:
            return (self, self.genericParameters)
        return None
    
    def as_protocol_composition_type(self):
        "Returns type-cast `self` if `self` describes a Protocol Composition type, otherwise returns `None`."
        return self if isinstance(self, ProtocolCompositionSwiftType) else None
    
    def as_tuple_type(self):
        "Returns type-cast `self` if `self` describes a Tuple type, otherwise returns `None`."
        return self if isinstance(self, TupleSwiftType) else None
    
    def as_optional_sugar_type(self):
        "Returns type-cast `self` if `self` describes a sugared `Optional<T>` type (i.e. `T?`), otherwise returns `None`."
        return self if isinstance(self, OptionalSwiftType) else None
    
    def as_implicitly_unwrapped_optional_sugar_type(self):
        "Returns type-cast `self` if `self` describes a sugared implicitly-unwrapped `Optional<T>` type (i.e. `T!`), otherwise returns `None`."
        return self if isinstance(self, ImplicitlyUnwrappedOptionalSwiftType) else None
    
    def as_array_sugar_type(self):
        "Returns type-cast `self` if `self` describes a sugared `Array<T>` type (i.e. `[T]`), otherwise returns `None`."
        return self if isinstance(self, ArraySwiftType) else None
    
    def as_dictionary_sugar_type(self):
        "Returns type-cast `self` if `self` describes a sugared `Dictionary<Key, Value>` type (i.e. `[Key: Value]`), otherwise returns `None`."
        return self if isinstance(self, DictionarySwiftType) else None
    
    #

    def wrap_optional(self):
        "Wraps `self` into a sugared `T?` Swift type."
        return SwiftType.optional(self)

    #

    def write(self, stream: SyntaxStream):
        """
        Writes the Swift syntax representation of this type as a string on a given
        syntax stream.
        """
        raise NotImplementedError()
    
    def to_string(self) -> str:
        "Returns the string representation of this Swift type via `self.write(stream)`."
        with io.StringIO() as buffer:
            stream = SyntaxStream(destination=buffer)
            self.write(stream)
            return buffer.getvalue()

    def requires_parenthesis(self) -> bool:
        """
        Returns True if parenthesis are required to make this type optional or
        nest it in in a protocol composition type to ensure correct syntax
        interpretation.
        """
        return False
    
    def isEquivalent(self, other: "SwiftType") -> bool:
        """
        Returns `True` if `self` and `other` map to the same canonical Swift type
        declaration.

        This can be used to check for type equivalence across syntax-sugared type
        combinations, e.g. `Int?` and `Optional<Int>`.
        """
        return self.desugared()._isEquivalent(other.desugared())
    
    def desugared(self) -> "SwiftType":
        "Returns the desugared representation of this type, e.g. `[Int?]` -> `Array<Optional<Int>>`."
        raise NotImplementedError("Must be overridden by subclasses.")
    
    def _isEquivalent(self, other: "SwiftType") -> bool:
        raise NotImplementedError("Must be overridden by subclasses.")

@dataclass(slots=True)
class NominalSwiftType(SwiftType):
    "A nominal Swift type, e.g. `Int` or `Array<Int>`."
    name: str
    genericParameters: list[SwiftType] | None

    def __init__(self, name, genericParameters: Iterable[SwiftType] | None = None):
        self.name = name
        self.genericParameters = list(genericParameters) if genericParameters is not None else None

    def write(self, stream: SyntaxStream):
        stream.write(self.name)
        if self.genericParameters is not None and len(self.genericParameters) > 0:
            stream.write("<")
            stream.with_separator(
                ", ",
                self.genericParameters,
                lambda s, p: p.write(s)
            )
            stream.write(">")

    def desugared(self) -> "NominalSwiftType":
        return NominalSwiftType(
            self.name,
            map(lambda t: t.desugared(), self.genericParameters) if self.genericParameters is not None and len(self.genericParameters) > 0 else None
        )
    
    def _isEquivalent(self, other: SwiftType) -> bool:
        if isinstance(other, NominalSwiftType):
            return self.__isEqual(other)
        
        return False
    
    def __isEqual(self, other: "NominalSwiftType") -> bool:
        if self.name != other.name:
            return False

        selfParams = self.genericParameters if self.genericParameters is not None else []
        otherParams = other.genericParameters if other.genericParameters is not None else []
        if len(selfParams) != len(otherParams):
            return False
        
        return all(lhs._isEquivalent(rhs) for lhs, rhs in zip(selfParams, otherParams))

@dataclass(slots=True)
class NestedSwiftType(SwiftType):
    "A nested Swift type, e.g. `Dictionary<String, Int>.Key`"
    types: list[NominalSwiftType]

    def __init__(self, types: Iterable[NominalSwiftType]):
        self.types = list(types)
        assert len(self.types) >= 2

    def write(self, stream: SyntaxStream):
        i = 0
        for comp in self.types:
            if i > 0:
                stream.write(".")
            comp.write(stream)
            i += 1
    
    def desugared(self) -> "NestedSwiftType":
        return NestedSwiftType(map(lambda t: t.desugared(), self.types))
    
    def _isEquivalent(self, other: SwiftType) -> bool:
        if isinstance(other, NestedSwiftType):
            return self.__isEqual(other)
        
        return False
    
    def __isEqual(self, other: "NestedSwiftType") -> bool:
        if len(self.types) != len(other.types):
            return False
        
        return all(lhs._isEquivalent(rhs) for lhs, rhs in zip(self.types, other.types))

@dataclass(slots=True)
class ProtocolCompositionSwiftType(SwiftType):
    "A protocol composition Swift type, e.g. `Protocol1 & Protocol2`."
    components: list[NominalSwiftType | NestedSwiftType]
    
    def __init__(self, components: Iterable[NominalSwiftType | NestedSwiftType]):
        self.components = list(components)
    
    def write(self, stream: SyntaxStream):
        stream.with_separator(
            " & ",
            self.components,
            lambda s, t: t.write(s)
        )
    
    def requires_parenthesis(self) -> bool:
        return True
    
    def desugared(self) -> "ProtocolCompositionSwiftType":
        return ProtocolCompositionSwiftType(
            map(lambda t: t.desugared(), self.components)
        )
    
    def _isEquivalent(self, other: SwiftType) -> bool:
        if isinstance(other, ProtocolCompositionSwiftType):
            return self.__isEqual(other)
        
        return False
    
    def __isEqual(self, other: "ProtocolCompositionSwiftType") -> bool:
        if len(self.components) != len(other.components):
            return False
        
        return all(lhs._isEquivalent(rhs) for lhs, rhs in zip(self.components, other.components))

@dataclass(slots=True)
class TupleSwiftType(SwiftType):
    """
    A Tuple Swift type, e.g. `(Int, String)` or `()`.

    Void is a special case of `TupleSwiftType` with zero types.
    """
    types: list[SwiftType]

    def __init__(self, types: Iterable[SwiftType]):
        self.types = list(types)
    
    def write(self, stream: SyntaxStream):
        stream.write("<")
        stream.with_separator(
            ", ",
            self.types,
            lambda s, t: t.write(s)
        )
        stream.write(">")
    
    def desugared(self) -> "TupleSwiftType | NominalSwiftType":
        if len(self.types) == 0:
            return SwiftType.typeName("Void")
        
        return TupleSwiftType(
            map(lambda t: t.desugared(), self.types)
        )
    
    def _isEquivalent(self, other: SwiftType) -> bool:
        if isinstance(other, TupleSwiftType):
            return self.__isEqual(other)
        
        return False
    
    def __isEqual(self, other: "TupleSwiftType") -> bool:
        if len(self.types) != len(other.types):
            return False
        
        return all(lhs._isEquivalent(rhs) for lhs, rhs in zip(self.types, other.types))

@dataclass(slots=True)
class FunctionSwiftType(SwiftType):
    "A type of a function, closure or method in Swift, e.g. `(Int, Bool) -> String`."
    parameters: list[SwiftType]
    returnType: SwiftType
    
    def __init__(self, parameters: Iterable[SwiftType], returnType: SwiftType):
        self.parameters = list(parameters)
        self.returnType = returnType
    
    def write(self, stream: SyntaxStream):
        stream.write("(")
        stream.with_separator(", ", self.parameters, lambda s, t: t.write(s))
        stream.write(") -> ")
        self.returnType.write(stream)
    
    def requires_parenthesis(self) -> bool:
        return True
    
    def desugared(self) -> "FunctionSwiftType":
        return FunctionSwiftType(
            parameters=map(lambda t: t.desugared(), self.parameters),
            returnType=self.returnType.desugared()
        )
    
    def _isEquivalent(self, other: SwiftType) -> bool:
        if isinstance(other, FunctionSwiftType):
            return self.__isEqual(other)
        
        return False
    
    def __isEqual(self, other: "FunctionSwiftType") -> bool:
        if len(self.parameters) != len(other.parameters):
            return False
        if not self.returnType._isEquivalent(other.returnType):
            return False
        
        return all(lhs._isEquivalent(rhs) for lhs, rhs in zip(self.parameters, other.parameters))

@dataclass(slots=True)
class OptionalSwiftType(SwiftType):
    """
    An optional Swift type, e.g. `String?`.
    
    This represents the syntax-sugared version of the canonically generic type
    syntax `Optional<T>`.
    """
    type: SwiftType
    
    def __init__(self, type: SwiftType):
        self.type = type
    
    def write(self, stream: SyntaxStream):
        if self.type.requires_parenthesis():
            stream.write("(")
        
        self.type.write(stream)
        
        if self.type.requires_parenthesis():
            stream.write(")")
        
        stream.write("?")
    
    def desugared(self) -> NominalSwiftType:
        return NominalSwiftType("Optional", [self.type.desugared()])
    
    def _isEquivalent(self, other: SwiftType) -> bool:
        if isinstance(other, OptionalSwiftType):
            return self.__isEqual(other)
        
        return False
    
    def __isEqual(self, other: "OptionalSwiftType") -> bool:
        return self.type._isEquivalent(other.type)

@dataclass(slots=True)
class ImplicitlyUnwrappedOptionalSwiftType(SwiftType):
    """
    An implicitly optional Swift type, e.g. `String!`.
    
    This represents the syntax-sugared version of the canonically generic type
    syntax `Optional<T>`.
    """
    type: SwiftType
    
    def __init__(self, type: SwiftType):
        self.type = type
    
    def write(self, stream: SyntaxStream):
        if self.type.requires_parenthesis():
            stream.write("(")
        
        self.type.write(stream)
        
        if self.type.requires_parenthesis():
            stream.write(")")
        
        stream.write("!")
    
    def desugared(self) -> "SwiftType":
        return ImplicitlyUnwrappedOptionalSwiftType(self.type.desugared())
    
    def _isEquivalent(self, other: SwiftType) -> bool:
        if isinstance(other, ImplicitlyUnwrappedOptionalSwiftType):
            return self.__isEqual(other)
        
        return False
    
    def __isEqual(self, other: "ImplicitlyUnwrappedOptionalSwiftType") -> bool:
        return self.type._isEquivalent(other.type)

@dataclass(slots=True)
class ArraySwiftType(SwiftType):
    """
    A Swift array type, e.g. `[Int]`.
    
    This represents the syntax-sugared version of the canonically generic type
    syntax `Array<T>`.
    """
    type: SwiftType

    def __init__(self, type: SwiftType):
        self.type = type
    
    def write(self, stream: SyntaxStream):
        stream.write("[")
        self.type.write(stream)
        stream.write("]")
    
    def desugared(self) -> "ArraySwiftType":
        return ArraySwiftType(self.type.desugared())

    def _isEquivalent(self, other: SwiftType) -> bool:
        if isinstance(other, ArraySwiftType):
            return self.__isEqual(other)
        
        return False
    
    def __isEqual(self, other: "ArraySwiftType") -> bool:
        return self.type._isEquivalent(other.type)

@dataclass(slots=True)
class DictionarySwiftType(SwiftType):
    """
    A Swift dictionary type, e.g. `[Int: String]`.
    
    This represents the syntax-sugared version of the canonically generic type
    syntax `Dictionary<Key, Value>`.
    """
    key: SwiftType
    value: SwiftType

    def __init__(self, key: SwiftType, value: SwiftType):
        self.key = key
        self.value = value
    
    def write(self, stream: SyntaxStream):
        stream.write("[")
        self.key.write(stream)
        stream.write(": ")
        self.value.write(stream)
        stream.write("]")
    
    def desugared(self) -> "DictionarySwiftType":
        return DictionarySwiftType(
            key=self.key.desugared(),
            value=self.value.desugared()
        )
    
    def _isEquivalent(self, other: SwiftType) -> bool:
        if isinstance(other, DictionarySwiftType):
            return self.__isEqual(other)
        
        return False
    
    def __isEqual(self, other: "DictionarySwiftType") -> bool:
        return self.key._isEquivalent(other.key) and self.value._isEquivalent(other.value)
