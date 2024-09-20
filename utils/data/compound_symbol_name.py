import re
from collections.abc import Sequence
from dataclasses import dataclass
from typing import Callable, Hashable, Iterable, Iterator, Optional, Tuple

from enum import Enum


class ComponentCase(Enum):
    """
    Describes the casing for a CompoundSymbolName.Component.
    """

    ANY = 0
    "Any casing is supported."

    AS_IS = 1
    "Component's casing must be maintained as-is during transformations."

    UPPER = 2
    "Component is pinned to UPPERCASE."

    LOWER = 3
    "Component is pinned to lowercase."

    CAPITALIZED = 4
    "Component is pinned to Capitalized."

    def change_case(self, string: str) -> str:
        """
        Changes a string to a case matching the one specified by 'self'. If the casing is ANY or AS_IS,
        the string is returned as-is.

        >>> ComponentCase.ANY.change_case("AString")
        'AString'
        >>> ComponentCase.UPPER.change_case("AString")
        'ASTRING'
        >>> ComponentCase.LOWER.change_case("AString")
        'astring'
        >>> ComponentCase.CAPITALIZED.change_case("AString")
        'Astring'
        >>> ComponentCase.AS_IS.change_case("AString")
        'AString'
        """
        match self:
            case ComponentCase.ANY:
                return string
            case ComponentCase.AS_IS:
                return string
            case ComponentCase.UPPER:
                return string.upper()
            case ComponentCase.LOWER:
                return string.lower()
            case ComponentCase.CAPITALIZED:
                return string.capitalize()

    def __or__(self, other):
        """
        Returns `other` if `self` is `ComponentCase.ANY`, `self` otherwise.

        >>> ComponentCase.ANY | ComponentCase.ANY
        <ComponentCase.ANY: 0>
        >>> ComponentCase.ANY | ComponentCase.AS_IS
        <ComponentCase.AS_IS: 1>
        >>> ComponentCase.UPPER | ComponentCase.LOWER
        <ComponentCase.UPPER: 2>
        """
        if self == ComponentCase.ANY:
            return other

        return self


_pascal_case_matcher = re.compile(
    r"((^[a-z]+)|([0-9]+)|([A-Z]{1}[a-z]+)|([A-Z]+(?=([A-Z][a-z])|($)|([0-9]))))"
)
_mixed_case_matcher = re.compile(
    r"((^[a-z]+)|([0-9]+)|(_+[a-z]+)|(_*[A-Z]{1}[a-z]+)|([A-Z]+(?=([A-Z][a-z])|($)|([0-9]))))"
)


@dataclass(repr=False, slots=True)
class CompoundSymbolName(Sequence["CompoundSymbolName.Component"], Hashable):
    """
    A type that is used to describe a symbol name as a collection of words
    that are stitched together as a string to produce a final identifier name.

    Can be used for camelCase, PascalCase, and snake_case strings.
    """

    @dataclass(frozen=True, repr=False, slots=True)
    class Component(Hashable):
        """
        A component of a CompoundSymbolName.
        """

        string: str
        "The string of this component"

        prefix: Optional[str] = None
        "An optional prefix that is prepended to this component when producing full strings."

        suffix: Optional[str] = None
        "An optional suffix that is appended to this component when producing full strings."

        joint_to_prev: Optional[str] = None
        "A string that is appended to this component if it follows another component in a symbol name."

        string_case: ComponentCase = ComponentCase.ANY
        "Specifies the suggested casing for this component."

        def __repr__(self) -> str:
            return (
                f"CompoundSymbolName.Component(string={self.string}, prefix={self.prefix}, suffix={self.suffix}, "
                f"joint_to_prev={self.joint_to_prev}, string_case={self.string_case})"
            )

        def __key(self):
            return (
                self.string,
                self.prefix,
                self.suffix,
                self.joint_to_prev,
                self.string_case,
            )

        def __hash__(self) -> int:
            return hash(self.__key())

        def __eq__(self, other: object) -> bool:
            if isinstance(other, CompoundSymbolName.Component):
                return self.__key() == other.__key()

            return False

        def copy(self) -> "CompoundSymbolName.Component":
            """
            Returns an exact copy of this Component.

            >>> CompoundSymbolName.Component(string="string", prefix="prefix",
            ...                              suffix="suffix", joint_to_prev="_",
            ...                              string_case=ComponentCase.LOWER).copy()
            CompoundSymbolName.Component(string=string, prefix=prefix, suffix=suffix, joint_to_prev=_, string_case=ComponentCase.LOWER)
            """
            return CompoundSymbolName.Component(
                self.string,
                self.prefix,
                self.suffix,
                self.joint_to_prev,
                self.string_case,
            )

        def with_string_only(
            self, string_case: ComponentCase | None = None
        ) -> "CompoundSymbolName.Component":
            """
            Returns a copy of this component with the same `self.string`, but no `prefix`, `suffix`, and `joint_to_prev`.

            If `string_case` is specified, string_case of the return is assigned that value, otherwise keeps the case
            of the current instance.
            """
            if string_case is None:
                string_case = self.string_case

            return CompoundSymbolName.Component(self.string, string_case=string_case)

        def with_prefix(self, prefix: str) -> "CompoundSymbolName.Component":
            return CompoundSymbolName.Component(
                self.string, prefix, self.suffix, self.joint_to_prev, self.string_case
            )

        def with_string(self, string: str) -> "CompoundSymbolName.Component":
            return CompoundSymbolName.Component(
                string, self.prefix, self.suffix, self.joint_to_prev, self.string_case
            )

        def replacing_in_string(
            self, old: str, new: str
        ) -> "CompoundSymbolName.Component":
            """
            Returns a copy of this `Component`, with any occurrence of `old` within
            `self.string` replaced with `new`.
            """
            return CompoundSymbolName.Component(
                self.string.replace(old, new),
                self.prefix,
                self.suffix,
                self.joint_to_prev,
                self.string_case,
            )

        def with_suffix(self, suffix: str) -> "CompoundSymbolName.Component":
            return CompoundSymbolName.Component(
                self.string, self.prefix, suffix, self.joint_to_prev, self.string_case
            )

        def with_joint_to_prev(self, joint_to_prev: str):
            return CompoundSymbolName.Component(
                self.string, self.prefix, self.suffix, joint_to_prev, self.string_case
            )

        def with_string_case(
            self, string_case: ComponentCase
        ) -> "CompoundSymbolName.Component":
            return CompoundSymbolName.Component(
                self.string, self.prefix, self.suffix, self.joint_to_prev, string_case
            )

        def lower(self, force=False) -> "CompoundSymbolName.Component":
            """
            Returns a copy of this component with all available strings lowercased.

            >>> CompoundSymbolName.Component(string='SyMBol').lower().to_string(has_previous=False)
            'symbol'

            >>> CompoundSymbolName.Component(string='SyMBol', prefix='pRef', suffix='SuFF', joint_to_prev='_Prev').lower().to_string(has_previous=True)
            '_prevprefsymbolsuff'

            If the component has a forced casing and 'force' is False, the operation returns an unaltered copy 'self':
            >>> CompoundSymbolName.Component(string='SyMBol', prefix='pRef', suffix='SuFF', joint_to_prev='_Prev',
            ...                              string_case=ComponentCase.AS_IS).lower().to_string(has_previous=True)
            '_PrevpRefSyMBolSuFF'

            If 'force' is True, the casing is forced to be lower-case but the string_case is reset to ComponentCase.ANY:
            >>> CompoundSymbolName.Component(string='SyMBol', prefix='pRef', suffix='SuFF', joint_to_prev='_Prev',
            ...                              string_case=ComponentCase.AS_IS).lower(force=True)
            CompoundSymbolName.Component(string=symbol, prefix=pref, suffix=suff, joint_to_prev=_prev, string_case=ComponentCase.ANY)
            """

            if not force and self.string_case != ComponentCase.ANY:
                return self

            prefix = self.prefix.lower() if self.prefix is not None else None
            suffix = self.suffix.lower() if self.suffix is not None else None
            joint_to_prev = (
                self.joint_to_prev.lower() if self.joint_to_prev is not None else None
            )

            return CompoundSymbolName.Component(
                self.string.lower(), prefix, suffix, joint_to_prev
            ).with_string_case(ComponentCase.ANY)

        def upper(self, force=False) -> "CompoundSymbolName.Component":
            """
            Returns a copy of this component with all available strings uppercased.

            >>> CompoundSymbolName.Component(string='SyMBol').upper().to_string(has_previous=False)
            'SYMBOL'

            >>> CompoundSymbolName.Component(string='SyMBol', prefix='pRef', suffix='SuFF', joint_to_prev='_Prev').upper().to_string(has_previous=True)
            '_PREVPREFSYMBOLSUFF'

            If the component has a forced casing and 'force' is False, the operation returns an unaltered copy 'self':
            >>> CompoundSymbolName.Component(string='SyMBol', prefix='pRef', suffix='SuFF', joint_to_prev='_Prev',
            ...                              string_case=ComponentCase.AS_IS).upper().to_string(has_previous=True)
            '_PrevpRefSyMBolSuFF'

            If 'force' is True, the casing is forced to be upper-case but the string_case is reset to ComponentCase.ANY:
            >>> CompoundSymbolName.Component(string='SyMBol', prefix='pRef', suffix='SuFF', joint_to_prev='_Prev',
            ...                              string_case=ComponentCase.LOWER).upper(force=True)
            CompoundSymbolName.Component(string=SYMBOL, prefix=PREF, suffix=SUFF, joint_to_prev=_PREV, string_case=ComponentCase.ANY)
            """

            if not force and self.string_case != ComponentCase.ANY:
                return self

            prefix = self.prefix.upper() if self.prefix is not None else None
            suffix = self.suffix.upper() if self.suffix is not None else None
            joint_to_prev = (
                self.joint_to_prev.upper() if self.joint_to_prev is not None else None
            )

            return CompoundSymbolName.Component(
                self.string.upper(), prefix, suffix, joint_to_prev
            ).with_string_case(ComponentCase.ANY)

        def to_string(self, has_previous: bool) -> str:
            """
            Returns a string representation of this component.

            Prefix, suffix and joint strings are only emitted if they are present:

            >>> CompoundSymbolName.Component(string='symbol').to_string(has_previous=False)
            'symbol'

            >>> CompoundSymbolName.Component(string='symbol', prefix='pref', suffix='suff').to_string(has_previous=False)
            'prefsymbolsuff'

            If the component has a 'joint_to_prev', it is appended only if has_previous is True:

            >>> CompoundSymbolName.Component(string='symbol', prefix='pref', joint_to_prev='_').to_string(has_previous=True)
            '_prefsymbol'

            If the component has a string_case different than ComponentCase.ANY or ComponentCase.AS_IS, the casing
            is adjusted according to the preference set:
            >>> CompoundSymbolName.Component(string='Symbol', prefix='Pref', suffix='Suff',
            ...                              joint_to_prev='_A',
            ...                              string_case=ComponentCase.LOWER).to_string(has_previous=True)
            '_aprefsymbolsuff'
            """

            result = ""

            if has_previous and self.joint_to_prev is not None:
                result += self.string_case.change_case(self.joint_to_prev)

            if self.prefix is not None:
                result += self.string_case.change_case(self.prefix)

            result += self.string_case.change_case(self.string)

            if self.suffix is not None:
                result += self.string_case.change_case(self.suffix)

            return result

        def startswith(self, string: str, has_previous: bool) -> bool:
            """
            Returns `True` if `self.to_string(has_previous=has_previous).startswith(string)`.
            """
            return self.to_string(has_previous=has_previous).startswith(string)

        def endswith(self, string: str, has_previous: bool) -> bool:
            """
            Returns `True` if `self.to_string(has_previous=has_previous).endswith(string)`.
            """
            return self.to_string(has_previous=has_previous).endswith(string)

    #

    components: list[Component]

    def __init__(self, components: Iterable[Component] | list[Component] | None = None):
        if components is None:
            self.components = []
            return
        if isinstance(components, list):
            self.components = components
        else:
            self.components = list(components)

        assert all(
            isinstance(comp, CompoundSymbolName.Component) for comp in self.components
        )

    def __eq__(self, other) -> bool:
        if isinstance(other, CompoundSymbolName):
            return self.components == other.components
        return False

    def __hash__(self) -> int:
        return hash(frozenset(self.components))

    def __getitem__(self, index):
        return self.components[index]

    def __len__(self) -> int:
        return len(self.components)

    def __iter__(self) -> Iterator[Component]:
        return self.components.__iter__()

    def __repr__(self) -> str:
        if len(self.components) == 0:
            return "CompoundSymbolName(components=[])"

        body = ",\n    ".join(f"{c}" for c in self.components)
        return f"CompoundSymbolName(components=[\n    {body}\n])"

    def __add__(self, value: "CompoundSymbolName") -> "CompoundSymbolName":
        """
        Returns the result of appending all the components of `value` onto `self`.
        Component properties are maintained on the resulting copy.

        >>> (CompoundSymbolName.from_string_list('a', 'symbol', 'name') + CompoundSymbolName.from_string_list('another', 'name')).camel_cased().to_string()
        'aSymbolNameAnotherName'
        """
        return CompoundSymbolName(self.components + value.components)

    @staticmethod
    def from_string_list(*strings: str) -> "CompoundSymbolName":
        components = map(lambda s: CompoundSymbolName.Component(s), strings)

        return CompoundSymbolName(components)

    @staticmethod
    def from_snake_case(string: str) -> "CompoundSymbolName":
        components = map(
            lambda s: CompoundSymbolName.Component(s, joint_to_prev="_"),
            string.split("_"),
        )

        return CompoundSymbolName(components)

    @classmethod
    def from_camel_case(cls, string: str) -> "CompoundSymbolName":
        """
        Alias for `CompoundSymbolName.from_pascal_case(<string>)`.

        Creates a new symbol name from a given `PascalCase` or `camelCase` string.

        >>> CompoundSymbolName.from_camel_case("APascalCaseString")
        CompoundSymbolName(components=[
            CompoundSymbolName.Component(string=A, prefix=None, suffix=None, joint_to_prev=None, string_case=ComponentCase.ANY),
            CompoundSymbolName.Component(string=Pascal, prefix=None, suffix=None, joint_to_prev=None, string_case=ComponentCase.ANY),
            CompoundSymbolName.Component(string=Case, prefix=None, suffix=None, joint_to_prev=None, string_case=ComponentCase.ANY),
            CompoundSymbolName.Component(string=String, prefix=None, suffix=None, joint_to_prev=None, string_case=ComponentCase.ANY)
        ])
        >>> CompoundSymbolName.from_camel_case("aCamelCaseString")
        CompoundSymbolName(components=[
            CompoundSymbolName.Component(string=a, prefix=None, suffix=None, joint_to_prev=None, string_case=ComponentCase.ANY),
            CompoundSymbolName.Component(string=Camel, prefix=None, suffix=None, joint_to_prev=None, string_case=ComponentCase.ANY),
            CompoundSymbolName.Component(string=Case, prefix=None, suffix=None, joint_to_prev=None, string_case=ComponentCase.ANY),
            CompoundSymbolName.Component(string=String, prefix=None, suffix=None, joint_to_prev=None, string_case=ComponentCase.ANY)
        ])
        """
        return cls.from_pascal_case(string)

    @classmethod
    def from_pascal_case(cls, string: str) -> "CompoundSymbolName":
        """
        Creates a new symbol name from a given `PascalCase` or `camelCase` string.

        >>> CompoundSymbolName.from_pascal_case("APascalCaseString")
        CompoundSymbolName(components=[
            CompoundSymbolName.Component(string=A, prefix=None, suffix=None, joint_to_prev=None, string_case=ComponentCase.ANY),
            CompoundSymbolName.Component(string=Pascal, prefix=None, suffix=None, joint_to_prev=None, string_case=ComponentCase.ANY),
            CompoundSymbolName.Component(string=Case, prefix=None, suffix=None, joint_to_prev=None, string_case=ComponentCase.ANY),
            CompoundSymbolName.Component(string=String, prefix=None, suffix=None, joint_to_prev=None, string_case=ComponentCase.ANY)
        ])
        >>> CompoundSymbolName.from_pascal_case("aCamelCaseString")
        CompoundSymbolName(components=[
            CompoundSymbolName.Component(string=a, prefix=None, suffix=None, joint_to_prev=None, string_case=ComponentCase.ANY),
            CompoundSymbolName.Component(string=Camel, prefix=None, suffix=None, joint_to_prev=None, string_case=ComponentCase.ANY),
            CompoundSymbolName.Component(string=Case, prefix=None, suffix=None, joint_to_prev=None, string_case=ComponentCase.ANY),
            CompoundSymbolName.Component(string=String, prefix=None, suffix=None, joint_to_prev=None, string_case=ComponentCase.ANY)
        ])
        """

        return cls.from_string_list(
            *(t[0] for t in _pascal_case_matcher.findall(string))
        )

    @classmethod
    def from_mixed_case(cls, string: str) -> "CompoundSymbolName":
        """
        Creates a new symbol name from a given `PascalCase` or `camelCase` string, with support for _ separators.

        >>> CompoundSymbolName.from_mixed_case("AMixedCase_String")
        CompoundSymbolName(components=[
            CompoundSymbolName.Component(string=A, prefix=None, suffix=None, joint_to_prev=None, string_case=ComponentCase.ANY),
            CompoundSymbolName.Component(string=Mixed, prefix=None, suffix=None, joint_to_prev=None, string_case=ComponentCase.ANY),
            CompoundSymbolName.Component(string=Case, prefix=None, suffix=None, joint_to_prev=None, string_case=ComponentCase.ANY),
            CompoundSymbolName.Component(string=String, prefix=None, suffix=None, joint_to_prev=_, string_case=ComponentCase.ANY)
        ])
        >>> CompoundSymbolName.from_mixed_case("a_mixedCase__String")
        CompoundSymbolName(components=[
            CompoundSymbolName.Component(string=a, prefix=None, suffix=None, joint_to_prev=None, string_case=ComponentCase.ANY),
            CompoundSymbolName.Component(string=mixed, prefix=None, suffix=None, joint_to_prev=_, string_case=ComponentCase.ANY),
            CompoundSymbolName.Component(string=Case, prefix=None, suffix=None, joint_to_prev=None, string_case=ComponentCase.ANY),
            CompoundSymbolName.Component(string=String, prefix=None, suffix=None, joint_to_prev=__, string_case=ComponentCase.ANY)
        ])
        """

        def analyze_component(string: str) -> CompoundSymbolName.Component:
            prefix = ""
            while string.startswith("_"):
                prefix += "_"
                string = string[1:]

            return CompoundSymbolName.Component(
                string,
                None,
                None,
                prefix if len(prefix) > 0 else None
            )

        string_list = [t[0] for t in _mixed_case_matcher.findall(string)]

        components = map(analyze_component, string_list)

        return CompoundSymbolName(components)

    def copy(self) -> "CompoundSymbolName":
        """
        Performs a deep copy of this CompoundSymbolName and its components.
        """
        return CompoundSymbolName(components=(c.copy() for c in self.components))

    def startswith(self, string: str) -> bool:
        """
        Returns True if the computed string for this symbol name starts with a provided string.

        >>> name = CompoundSymbolName.from_snake_case('D3D12_DRED_VERSION')
        >>> name.startswith('D3D12')
        True
        >>> name.startswith('D3D12_DRED')
        True
        >>> name.startswith('DXGI')
        False

        If the symbol name is empty, only empty strings match:

        >>> name = CompoundSymbolName([])
        >>> name.startswith('D3D12')
        False
        >>> name.startswith('')
        True
        """

        if len(self) == 0:
            return string == ""

        return self.to_string().startswith(string)

    def endswith(self, string: str) -> bool:
        """
        Returns True if the computed string for this symbol name ends with a provided string.

        >>> name = CompoundSymbolName.from_snake_case('D3D12_DRED_VERSION')
        >>> name.endswith('VERSION')
        True
        >>> name.endswith('DRED_VERSION')
        True
        >>> name.endswith('DXGI')
        False

        If the symbol name is empty, only empty strings match:

        >>> name = CompoundSymbolName([])
        >>> name.endswith('D3D12')
        False
        >>> name.endswith('')
        True
        """

        if len(self) == 0:
            return string == ""

        return self.to_string().endswith(string)

    def adding_component(
        self,
        string: str,
        prefix: str | None = None,
        suffix: str | None = None,
        joint_to_prev: str | None = None,
        string_case: ComponentCase = ComponentCase.ANY,
    ) -> "CompoundSymbolName":
        copy = self.copy()
        copy.components.append(
            CompoundSymbolName.Component(
                string, prefix, suffix, joint_to_prev, string_case
            )
        )
        return copy

    def prepending_component(
        self,
        string: str,
        prefix: str | None = None,
        suffix: str | None = None,
        joint_to_prev: str | None = None,
        string_case: ComponentCase = ComponentCase.ANY,
    ) -> "CompoundSymbolName":
        copy = self.copy()
        copy.components.insert(
            0,
            CompoundSymbolName.Component(
                string, prefix, suffix, joint_to_prev, string_case
            ),
        )
        return copy

    def mapping_components(
        self,
        mapper: Callable[
            [int, "CompoundSymbolName.Component"], "CompoundSymbolName.Component"
        ],
    ):
        return CompoundSymbolName(mapper(c[0], c[1]) for c in enumerate(self))

    def split(
        self,
        predicate: Callable[[int, "CompoundSymbolName.Component"], bool],
        include_separator: bool = False,
    ) -> list["CompoundSymbolName"]:
        """
        Splits this CompoundSymbolName across components based on a predicate that receives the component and its index
        on the component list.

        If include_separator is True, the separator components are included in the resulting list, otherwise they are
        omitted.

        >>> CompoundSymbolName.from_snake_case('a_symbol_name').split(lambda i,c: c.string == 'symbol')
        [CompoundSymbolName(components=[
            CompoundSymbolName.Component(string=a, prefix=None, suffix=None, joint_to_prev=_, string_case=ComponentCase.ANY)
        ]), CompoundSymbolName(components=[
            CompoundSymbolName.Component(string=name, prefix=None, suffix=None, joint_to_prev=_, string_case=ComponentCase.ANY)
        ])]
        >>> CompoundSymbolName.from_snake_case('a_symbol_name').split(lambda i,c: c.string == 'symbol', include_separator=True)
        [CompoundSymbolName(components=[
            CompoundSymbolName.Component(string=a, prefix=None, suffix=None, joint_to_prev=_, string_case=ComponentCase.ANY)
        ]), CompoundSymbolName(components=[
            CompoundSymbolName.Component(string=symbol, prefix=None, suffix=None, joint_to_prev=_, string_case=ComponentCase.ANY)
        ]), CompoundSymbolName(components=[
            CompoundSymbolName.Component(string=name, prefix=None, suffix=None, joint_to_prev=_, string_case=ComponentCase.ANY)
        ])]
        """
        current: CompoundSymbolName | None = None
        result = list()

        for i, comp in enumerate(self):
            if predicate(i, comp):
                if current is not None:
                    result.append(current)
                    current = None

                if include_separator:
                    result.append(CompoundSymbolName([comp.copy()]))
            else:
                if current is None:
                    current = CompoundSymbolName([comp.copy()])
                else:
                    current.components.append(comp.copy())

        if current is not None:
            result.append(current)

        return result

    def lower(self, force=False) -> "CompoundSymbolName":
        """
        Returns a copy of this CompoundSymbolName with every component lower-cased.

        If this compound symbol name has any component where the casing is pinned to some value other than
        ComponentCase.ANY, the casing of that element is manitained.

        >>> c = CompoundSymbolName.from_string_list('A', 'Symbol', 'NAME')
        >>> c.components[2] = c.components[2].with_string_case(ComponentCase.UPPER)
        >>> c.lower(force=False).to_string()
        'asymbolNAME'

        Passing force=True resets the casing of the components to ComponentCase.ANY and the string is lowercased:
        >>> c.lower(force=True).to_string()
        'asymbolname'
        """

        return CompoundSymbolName(c.copy().lower(force=force) for c in self)

    def upper(self, force=False) -> "CompoundSymbolName":
        """
        Returns a copy of this CompoundSymbolName with every component upper-cased.

        If this compound symbol name has any component where the casing is pinned to some value other than
        ComponentCase.ANY, the casing of that element is manitained.

        >>> c = CompoundSymbolName.from_string_list('A', 'Symbol', 'name')
        >>> c.components[2] = c.components[2].with_string_case(ComponentCase.LOWER)
        >>> c.upper(force=False).to_string()
        'ASYMBOLname'

        Passing force=True resets the casing of the components to ComponentCase.ANY and the string is uppercased:
        >>> c.upper(force=True).to_string()
        'ASYMBOLNAME'
        """

        return CompoundSymbolName(c.copy().upper(force=force) for c in self)

    def removing_prefixes(
        self, prefixes: list[str], case_sensitive=True
    ) -> "CompoundSymbolName":
        """
        Returns a new CompoundSymbolName with any compound whose string matches a string in 'prefixes' removed.

        The matching can be done in a case-sensitive or insensitive manner according to the `case_sensitive` parameter.
        Defaults to case-sensitive.

        >>> name = CompoundSymbolName.from_snake_case('D3D12_DRED_VERSION')
        >>> name.removing_prefixes(['D3D12']).to_string()
        'DRED_VERSION'

        >>> name = CompoundSymbolName.from_snake_case('d3d12_dred_version')
        >>> name.removing_prefixes(['D3D12'], case_sensitive=False).to_string()
        'dred_version'
        """

        index = 0
        for comp in self:
            if not case_sensitive:
                for prefix in prefixes:
                    if comp.string.lower() == prefix.lower():
                        index += 1
                    else:
                        break
            else:
                if comp.string in prefixes:
                    index += 1
                else:
                    break

        return CompoundSymbolName(self.components[index:])

    def removing_common(
        self,
        other: "CompoundSymbolName",
        case_sensitive: bool = True,
        detect_plurals: bool = True,
    ) -> Tuple["CompoundSymbolName", Optional["CompoundSymbolName"]]:
        """
        Returns a new CompoundSymbolName with the common prefix between it and another CompoundSymbolName removed.

        In case the generated name would produce an invalid Swift identifier, like starting with a digit instead of a letter, an extra
        prefix is provided as a second element to the return's tuple:

        >>> enum      = CompoundSymbolName.from_snake_case('D3D12_DRED_VERSION')
        >>> enum_case = CompoundSymbolName.from_snake_case('D3D12_DRED_VERSION_1_0')
        >>> enum_case.removing_common(enum)
        (CompoundSymbolName(components=[
            CompoundSymbolName.Component(string=1, prefix=None, suffix=None, joint_to_prev=_, string_case=ComponentCase.ANY),
            CompoundSymbolName.Component(string=0, prefix=None, suffix=None, joint_to_prev=_, string_case=ComponentCase.ANY)
        ]),
        CompoundSymbolName(components=[
            CompoundSymbolName.Component(string=VERSION, prefix=None, suffix=None, joint_to_prev=_, string_case=ComponentCase.ANY)
        ]))

        Optionally allows detecting differences in plurals, e.g.

        >>> enum      = CompoundSymbolName.from_snake_case('D3D12_RAY_FLAGS')
        >>> enum_case = CompoundSymbolName.from_snake_case('D3D12_RAY_FLAG_NONE')
        >>> enum_case.removing_common(enum, detect_plurals=True)[0]
        CompoundSymbolName(components=[
            CompoundSymbolName.Component(string=NONE, prefix=None, suffix=None, joint_to_prev=_, string_case=ComponentCase.ANY)
        ])

        >>> enum_case.removing_common(enum, detect_plurals=False)[0]
        CompoundSymbolName(components=[
            CompoundSymbolName.Component(string=FLAG, prefix=None, suffix=None, joint_to_prev=_, string_case=ComponentCase.ANY),
            CompoundSymbolName.Component(string=NONE, prefix=None, suffix=None, joint_to_prev=_, string_case=ComponentCase.ANY)
        ])
        """

        prefix_index = 0
        for index in range(min(len(self), len(other))):
            if detect_plurals:
                if self[index].string.lower() + "s" == other[index].string.lower():
                    prefix_index += 1
                    continue
                if self[index].string.lower() == other[index].string.lower() + "s":
                    prefix_index += 1
                    continue

            if case_sensitive:
                if self[index].string != other[index].string:
                    break
            else:
                if self[index].string.lower() != other[index].string.lower():
                    break

            prefix_index += 1

        # Detect names starting with digits and relax the prefix index until we
        # reach a name that does not start with a digit.
        extra_prefix_index = prefix_index
        while extra_prefix_index > 0 and self[extra_prefix_index].string[0].isdigit():
            extra_prefix_index -= 1

        new_name = CompoundSymbolName(self.components[prefix_index:])

        if extra_prefix_index != prefix_index:
            prefix_name = CompoundSymbolName(
                self.components[extra_prefix_index:prefix_index]
            )

            return new_name, prefix_name
        else:
            return new_name, None

    def lower_snake_cased(self, force=False) -> "CompoundSymbolName":
        """
        Returns a new compound name where each component is a component from this
        compound name that when put together with to_string() forms a `lower_case_snake_cased_string`.

        >>> CompoundSymbolName.from_string_list('A', 'Symbol', 'Name').lower_snake_cased().to_string()
        'a_symbol_name'

        If this compound symbol name has any component where the casing is pinned to some value other than
        ComponentCase.ANY, the casing of that element is maintained.

        >>> c = CompoundSymbolName.from_string_list('A', 'Symbol', 'NAME')
        >>> c.components[2] = c.components[2].with_string_case(ComponentCase.UPPER)
        >>> c.lower_snake_cased(force=False).to_string()
        'a_symbol_NAME'

        Passing force=True resets the casing of the components to ComponentCase.ANY and the string is lowercased:
        >>> c.lower_snake_cased(force=True).to_string()
        'a_symbol_name'
        """

        return CompoundSymbolName(
            comp.with_string_only().lower(force=force).with_joint_to_prev("_")
            for comp in self
        )

    def upper_snake_cased(self, force=False) -> "CompoundSymbolName":
        """
        Returns a new compound name where each component is a component from this
        compound name that when put together with to_string() forms an `UPPER_CASE_SNAKE_CASED_STRING`.

        >>> CompoundSymbolName.from_string_list('A', 'Symbol', 'Name').upper_snake_cased().to_string()
        'A_SYMBOL_NAME'

        If this compound symbol name has any component where the casing is pinned to some value other than
        ComponentCase.ANY, the casing of that element is maintained.

        >>> c = CompoundSymbolName.from_string_list('A', 'Symbol', 'name')
        >>> c.components[2] = c.components[2].with_string_case(ComponentCase.LOWER)
        >>> c.upper_snake_cased(force=False).to_string()
        'A_SYMBOL_name'

        Passing force=True resets the casing of the components to ComponentCase.ANY and the string is lowercased:
        >>> c.upper_snake_cased(force=True).to_string()
        'A_SYMBOL_NAME'
        """

        return CompoundSymbolName(
            comp.with_string_only().upper(force=force).with_joint_to_prev("_")
            for comp in self
        )

    def pascal_cased(self) -> "CompoundSymbolName":
        """
        Returns a new compound name where each component is a component from this
        compound name that when put together with to_string() forms a `PascalCaseString`.

        >>> CompoundSymbolName.from_string_list('a', 'symbol', 'name').pascal_cased().to_string()
        'ASymbolName'
        """
        return CompoundSymbolName(
            CompoundSymbolName.Component(comp.string.capitalize()) for comp in self
        )

    def camel_cased(self, digit_separator: str = "_") -> "CompoundSymbolName":
        """
        Returns a new compound name where each component is a component from this
        compound name that when put together with to_string() forms a `camelCaseString`.

        >>> CompoundSymbolName.from_string_list('a', 'symbol', 'name').camel_cased().to_string()
        'aSymbolName'

        If two adjacent components have digits on each end, digit_separator will be added as a
        joint to the second component:

        >>> CompoundSymbolName.from_string_list('target', '1', '0').camel_cased().to_string()
        'target1_0'

        An empty digit separator string can be used to omit this behavior:

        >>> CompoundSymbolName.from_string_list('target', '1', '0').camel_cased(digit_separator="").to_string()
        'target10'
        """

        result: list[CompoundSymbolName.Component] = []

        for i, comp in enumerate(self.components):
            new_comp = comp.with_string_only().lower()

            if i > 0:
                new_comp = new_comp.with_string(new_comp.string.capitalize())

                if (
                    new_comp.to_string(True)[0].isdigit()
                    and self[i - 1].to_string(i > 1)[-1].isdigit()
                ):
                    new_comp = new_comp.with_joint_to_prev(digit_separator)

            result.append(new_comp)

        return CompoundSymbolName(components=result)

    def appending(self, other: "CompoundSymbolName") -> "CompoundSymbolName":
        """
        Returns the result of appending all the components of `other` onto `self`.
        Component properties are maintained on the resulting copy.

        >>> CompoundSymbolName.from_string_list('a', 'symbol', 'name').appending(CompoundSymbolName.from_string_list('another', 'name')).camel_cased().to_string()
        'aSymbolNameAnotherName'
        """
        return self + other

    def to_string(self) -> str:
        return "".join(c[1].to_string(c[0] > 0) for c in enumerate(self.components))


if __name__ == "__main__":
    import doctest

    doctest.testmod(optionflags=doctest.NORMALIZE_WHITESPACE)
