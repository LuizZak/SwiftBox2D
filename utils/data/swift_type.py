import io
from dataclasses import dataclass
from typing import Iterable

from utils.text.syntax_stream import SyntaxStream


@dataclass(slots=True)
class SwiftType:
    """Base class for Swift types."""

    # Type factories

    @classmethod
    def bool_type(cls) -> "NominalSwiftType":
        """Returns the built-in Bool Swift type."""
        return cls.type_name("Bool")

    @classmethod
    def void_type(cls) -> "TupleSwiftType":
        """Returns the built-in Void Swift type, i.e. `()`."""
        return TupleSwiftType([])

    @classmethod
    def type_name(cls, name: str) -> "NominalSwiftType":
        """Creates a nominal Swift type, e.g. `Int`."""
        return NominalSwiftType(name)

    @classmethod
    def generic(
        cls, name: str, params: Iterable["SwiftType | str"]
    ) -> "NominalSwiftType":
        """Creates a generic Swift type, e.g. `MyType<Int>`."""
        return NominalSwiftType(name, cls._process_types(params))

    @classmethod
    def optional(cls, type: "SwiftType | str") -> "OptionalSwiftType":
        """Creates an Optional sugar Swift type, e.g. `Int?`"""
        return OptionalSwiftType(cls._process_type(type))

    @classmethod
    def implicitly_unwrapped_optional(
        cls, type: "SwiftType | str"
    ) -> "ImplicitlyUnwrappedOptionalSwiftType":
        """Creates an implicitly-unwrapped Optional sugar Swift type, e.g. `Int!`"""
        return ImplicitlyUnwrappedOptionalSwiftType(cls._process_type(type))

    @classmethod
    def array(cls, type: "SwiftType | str") -> "ArraySwiftType":
        """Creates an Array sugar Swift type, e.g. `[Int]`."""
        return ArraySwiftType(cls._process_type(type))

    @classmethod
    def dictionary(
        cls, key: "SwiftType | str", value: "SwiftType | str"
    ) -> "DictionarySwiftType":
        """Creates a Dictionary sugar Swift type, e.g. `[Int: String]`."""
        return DictionarySwiftType(cls._process_type(key), cls._process_type(value))

    @classmethod
    def function(
        cls, parameters: Iterable["SwiftType | str"], return_type: "SwiftType | str"
    ) -> "FunctionSwiftType":
        """Creates a Function Swift type, e.g. `(Int) -> String`."""
        return FunctionSwiftType(
            cls._process_types(parameters), cls._process_type(return_type)
        )

    @classmethod
    def tuple(cls, types: Iterable["SwiftType | str"]) -> "TupleSwiftType":
        """Creates a tuple Swift type, e.g. `(Int, String)`."""
        return TupleSwiftType(cls._process_types(types))

    @classmethod
    def protocol_composition(
        cls, components: Iterable["NominalSwiftType | NestedSwiftType"]
    ) -> "ProtocolCompositionSwiftType":
        """Creates a protocol composition Swift type, e.g. `Protocol1 & Protocol2`."""
        return ProtocolCompositionSwiftType(components)

    @classmethod
    def _process_type(cls, type: "SwiftType | str") -> "SwiftType":
        if isinstance(type, SwiftType):
            return type

        return NominalSwiftType(type)

    @classmethod
    def _process_types(cls, types: Iterable["SwiftType | str"]) -> list["SwiftType"]:
        return [cls._process_type(type) for type in types]

    # Methods

    def is_function_type(self):
        """Returns `True` if `self` describes a Function type."""
        return isinstance(self, FunctionSwiftType)

    def is_typename_type(self):
        """Returns `True` if `self` describes a Nominal type."""
        return isinstance(self, NominalSwiftType)

    def is_nested_type(self):
        """Returns `True` if `self` describes a Nested Nominal type."""
        return isinstance(self, NestedSwiftType)

    def is_generic_type(self):
        """Returns `True` if `self` describes a Nominal type with generic arguments."""
        if isinstance(self, NominalSwiftType):
            return self.generic_parameters is not None
        return False

    def is_protocol_composition_type(self):
        """Returns `True` if `self` describes a Protocol Composition type."""
        return isinstance(self, ProtocolCompositionSwiftType)

    def is_tuple_type(self):
        """Returns `True` if `self` describes a Tuple type."""
        return isinstance(self, TupleSwiftType)

    def is_optional_sugar_type(self):
        """Returns `True` if `self` describes a sugared `Optional<T>` type (i.e. `T?`)."""
        return isinstance(self, OptionalSwiftType)

    def is_implicitly_unwrapped_optional_sugar_type(self):
        """Returns `True` if `self` describes a sugared implicitly-unwrapped `Optional<T>` type (i.e. `T!`)."""
        return isinstance(self, ImplicitlyUnwrappedOptionalSwiftType)

    def is_array_sugar_type(self):
        """Returns `True` if `self` describes a sugared `Array<T>` type (i.e. `[T]`)."""
        return isinstance(self, ArraySwiftType)

    def is_dictionary_sugar_type(self):
        """Returns `True` if `self` describes a sugared `Dictionary<Key, Value>` type (i.e. `[Key: Value]`)."""
        return isinstance(self, DictionarySwiftType)

    #

    def as_function_type(self):
        """Returns type-cast `self` if `self` describes a Function type, otherwise returns `None`."""
        return self if isinstance(self, FunctionSwiftType) else None

    def as_typename_type(self):
        """Returns type-cast `self` if `self` describes a Nominal type, otherwise returns `None`."""
        return self if isinstance(self, NominalSwiftType) else None

    def as_nested_type(self):
        """Returns type-cast `self` if `self` describes a Nested Nominal type, otherwise returns `None`."""
        return self if isinstance(self, NestedSwiftType) else None

    def as_generic_type(self):
        """Returns type-cast `self` and a list of generic arguments if `self` describes a Nominal type with generic arguments, otherwise returns `None`."""
        if isinstance(self, NominalSwiftType) and self.generic_parameters is not None:
            return self, self.generic_parameters
        return None

    def as_protocol_composition_type(self):
        """Returns type-cast `self` if `self` describes a Protocol Composition type, otherwise returns `None`."""
        return self if isinstance(self, ProtocolCompositionSwiftType) else None

    def as_tuple_type(self):
        """Returns type-cast `self` if `self` describes a Tuple type, otherwise returns `None`."""
        return self if isinstance(self, TupleSwiftType) else None

    def as_optional_sugar_type(self):
        """Returns type-cast `self` if `self` describes a sugared `Optional<T>` type (i.e. `T?`), otherwise returns `None`."""
        return self if isinstance(self, OptionalSwiftType) else None

    def as_implicitly_unwrapped_optional_sugar_type(self):
        """Returns type-cast `self` if `self` describes a sugared implicitly-unwrapped `Optional<T>` type (i.e. `T!`), otherwise returns `None`."""
        return self if isinstance(self, ImplicitlyUnwrappedOptionalSwiftType) else None

    def as_array_sugar_type(self):
        """Returns type-cast `self` if `self` describes a sugared `Array<T>` type (i.e. `[T]`), otherwise returns `None`."""
        return self if isinstance(self, ArraySwiftType) else None

    def as_dictionary_sugar_type(self):
        """Returns type-cast `self` if `self` describes a sugared `Dictionary<Key, Value>` type (i.e. `[Key: Value]`), otherwise returns `None`."""
        return self if isinstance(self, DictionarySwiftType) else None

    #

    def wrap_optional(self):
        """Wraps `self` into a sugared `T?` Swift type."""
        return SwiftType.optional(self)

    #

    def write(self, stream: SyntaxStream):
        """
        Writes the Swift syntax representation of this type as a string on a given
        syntax stream.
        """
        raise NotImplementedError()

    def to_string(self) -> str:
        """Returns the string representation of this Swift type via `self.write(stream)`."""
        with io.StringIO() as buffer:
            stream = SyntaxStream(destination=buffer)
            self.write(stream)
            return buffer.getvalue()

    def __str__(self):
        return self.to_string()

    def requires_parenthesis(self) -> bool:
        """
        Returns True if parenthesis are required to make this type optional or
        nest it in in a protocol composition type to ensure correct syntax
        interpretation.
        """
        return False

    def is_equivalent(self, other: "SwiftType") -> bool:
        """
        Returns `True` if `self` and `other` map to the same canonical Swift type
        declaration.

        This can be used to check for type equivalence across syntax-sugared type
        combinations, e.g. `Int?` and `Optional<Int>`.
        """
        return self.desugared()._is_equivalent(other.desugared())

    def desugared(self) -> "SwiftType":
        """Returns the desugared representation of this type, e.g. `[Int?]` -> `Array<Optional<Int>>`."""
        raise NotImplementedError("Must be overridden by subclasses.")

    def _is_equivalent(self, other: "SwiftType") -> bool:
        raise NotImplementedError("Must be overridden by subclasses.")


@dataclass(slots=True)
class NominalSwiftType(SwiftType):
    """A nominal Swift type, e.g. `Int` or `Array<Int>`."""

    name: str
    generic_parameters: list[SwiftType] | None

    def __init__(self, name, generic_parameters: Iterable[SwiftType] | None = None):
        self.name = name
        self.generic_parameters = (
            list(generic_parameters) if generic_parameters is not None else None
        )

    def write(self, stream: SyntaxStream):
        stream.write(self.name)
        if self.generic_parameters is not None and len(self.generic_parameters) > 0:
            stream.write("<")
            stream.with_separator(
                ", ", self.generic_parameters, lambda s, p: p.write(s)
            )
            stream.write(">")

    def desugared(self) -> "NominalSwiftType":
        return NominalSwiftType(
            self.name,
            map(lambda t: t.desugared(), self.generic_parameters)
            if self.generic_parameters is not None and len(self.generic_parameters) > 0
            else None,
        )

    def _is_equivalent(self, other: SwiftType) -> bool:
        if isinstance(other, NominalSwiftType):
            return self._is_equal(other)

        return False

    def _is_equal(self, other: "NominalSwiftType") -> bool:
        if self.name != other.name:
            return False

        self_params = (
            self.generic_parameters if self.generic_parameters is not None else []
        )
        other_params = (
            other.generic_parameters if other.generic_parameters is not None else []
        )
        if len(self_params) != len(other_params):
            return False

        return all(
            lhs._is_equivalent(rhs) for lhs, rhs in zip(self_params, other_params)
        )


@dataclass(slots=True)
class NestedSwiftType(SwiftType):
    """A nested Swift type, e.g. `Dictionary<String, Int>.Key`"""

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

    def _is_equivalent(self, other: SwiftType) -> bool:
        if isinstance(other, NestedSwiftType):
            return self.__is_equal(other)

        return False

    def __is_equal(self, other: "NestedSwiftType") -> bool:
        if len(self.types) != len(other.types):
            return False

        return all(lhs._is_equivalent(rhs) for lhs, rhs in zip(self.types, other.types))


@dataclass(slots=True)
class ProtocolCompositionSwiftType(SwiftType):
    """A protocol composition Swift type, e.g. `Protocol1 & Protocol2`."""

    components: list[NominalSwiftType | NestedSwiftType]

    def __init__(self, components: Iterable[NominalSwiftType | NestedSwiftType]):
        self.components = list(components)

    def write(self, stream: SyntaxStream):
        stream.with_separator(" & ", self.components, lambda s, t: t.write(s))

    def requires_parenthesis(self) -> bool:
        return True

    def desugared(self) -> "ProtocolCompositionSwiftType":
        return ProtocolCompositionSwiftType(
            map(lambda t: t.desugared(), self.components)
        )

    def _is_equivalent(self, other: SwiftType) -> bool:
        if isinstance(other, ProtocolCompositionSwiftType):
            return self.__is_equal(other)

        return False

    def __is_equal(self, other: "ProtocolCompositionSwiftType") -> bool:
        if len(self.components) != len(other.components):
            return False

        return all(
            lhs._is_equivalent(rhs)
            for lhs, rhs in zip(self.components, other.components)
        )


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
        stream.write("(")
        stream.with_separator(", ", self.types, lambda s, t: t.write(s))
        stream.write(")")

    def desugared(self) -> "TupleSwiftType | NominalSwiftType":
        if len(self.types) == 0:
            return SwiftType.type_name("Void")

        return TupleSwiftType(map(lambda t: t.desugared(), self.types))

    def _is_equivalent(self, other: SwiftType) -> bool:
        if isinstance(other, TupleSwiftType):
            return self.__is_equal(other)

        return False

    def __is_equal(self, other: "TupleSwiftType") -> bool:
        if len(self.types) != len(other.types):
            return False

        return all(lhs._is_equivalent(rhs) for lhs, rhs in zip(self.types, other.types))


@dataclass(slots=True)
class FunctionSwiftType(SwiftType):
    """A type of a function, closure or method in Swift, e.g. `(Int, Bool) -> String`."""

    parameters: list[SwiftType]
    return_type: SwiftType

    def __init__(self, parameters: Iterable[SwiftType], return_type: SwiftType):
        self.parameters = list(parameters)
        self.return_type = return_type

    def write(self, stream: SyntaxStream):
        stream.write("(")
        stream.with_separator(", ", self.parameters, lambda s, t: t.write(s))
        stream.write(") -> ")
        self.return_type.write(stream)

    def requires_parenthesis(self) -> bool:
        return True

    def desugared(self) -> "FunctionSwiftType":
        return FunctionSwiftType(
            parameters=map(lambda t: t.desugared(), self.parameters),
            return_type=self.return_type.desugared(),
        )

    def _is_equivalent(self, other: SwiftType) -> bool:
        if isinstance(other, FunctionSwiftType):
            return self.__is_equal(other)

        return False

    def __is_equal(self, other: "FunctionSwiftType") -> bool:
        if len(self.parameters) != len(other.parameters):
            return False
        if not self.return_type._is_equivalent(other.return_type):
            return False

        return all(
            lhs._is_equivalent(rhs)
            for lhs, rhs in zip(self.parameters, other.parameters)
        )


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

    def _is_equivalent(self, other: SwiftType) -> bool:
        if isinstance(other, OptionalSwiftType):
            return self.__is_equal(other)

        return False

    def __is_equal(self, other: "OptionalSwiftType") -> bool:
        return self.type._is_equivalent(other.type)


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

    def _is_equivalent(self, other: SwiftType) -> bool:
        if isinstance(other, ImplicitlyUnwrappedOptionalSwiftType):
            return self.__is_equal(other)

        return False

    def __is_equal(self, other: "ImplicitlyUnwrappedOptionalSwiftType") -> bool:
        return self.type._is_equivalent(other.type)


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

    def _is_equivalent(self, other: SwiftType) -> bool:
        if isinstance(other, ArraySwiftType):
            return self.__is_equal(other)

        return False

    def __is_equal(self, other: "ArraySwiftType") -> bool:
        return self.type._is_equivalent(other.type)


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
            key=self.key.desugared(), value=self.value.desugared()
        )

    def _is_equivalent(self, other: SwiftType) -> bool:
        if isinstance(other, DictionarySwiftType):
            return self.__is_equal(other)

        return False

    def __is_equal(self, other: "DictionarySwiftType") -> bool:
        return self.key._is_equivalent(other.key) and self.value._is_equivalent(
            other.value
        )
