import re
from typing import Iterable, Tuple

from utils.converters.base_word_capitalizer import BaseWordCapitalizer
from utils.data.c_decl_kind import CDeclKind
from utils.data.compound_symbol_name import ComponentCase, CompoundSymbolName
from utils.data.generator_config import GeneratorConfig


class SymbolNameFormatter:
    symbol_case_settings: GeneratorConfig.Declarations.SymbolCasingSettings
    "Default symbol casing settings to use when first formatting symbol names, before extra capitalization work is done."

    capitalizers: list[BaseWordCapitalizer]
    """
    Capitalizers for words that are contained within terms.
    When capitalizers report a substring to capitalize, the string is split and
    the match substring portion pinned to uppercase.

    - note: Capitalization implicitly splits components in a CompoundSymbolName
    into separate components.
    - note: If more than one entry in this list match a single component, the
    entry that matches earliest in the string is chosen.
    """

    # TODO: Figure out a better way to automatically recognize joined symbol name.
    words_to_split: list[re.Pattern]
    """
    Use multi-word regex when a standalone word might lead to unintended matches in compound words.
    eg: D2D1_COLORMANAGEMENT_PROP
    would be an entry like:
    `re.compile(r"(Color)(Management)", flags=re.IGNORECASE)`

    - NOTE: Regex are applied recursively to split segments, so a simple regex that has a single capture group will lead to recursion errors.
    """

    terms_to_snake_case_after: list[str]
    """
    List of camelCase terms to detect and split into a trailing snake_case.

    E.g.: To split 'x86Sse2' into x86_sse2, provide `terms_to_snake_case=["x86"]`.

    - note: Matching is case-sensitive.
    """

    def __init__(
        self,
        symbol_case_settings: GeneratorConfig.Declarations.SymbolCasingSettings,
        capitalizers: Iterable[BaseWordCapitalizer] | None = None,
        words_to_split: Iterable[re.Pattern] | None = None,
        terms_to_snake_case_after: Iterable[str] | None = None,
    ):
        if capitalizers is None:
            capitalizers = []
        if words_to_split is None:
            words_to_split = []
        if terms_to_snake_case_after is None:
            terms_to_snake_case_after = []

        self.symbol_case_settings = symbol_case_settings
        self.capitalizers = list(capitalizers)
        self.words_to_split = list(words_to_split)
        self.terms_to_snake_case_after = list(terms_to_snake_case_after)

    @classmethod
    def from_config(cls, config: GeneratorConfig.Declarations.SwiftNameFormatting):
        def splitter_pattern(pattern: str):
            regex = re.compile(pattern, flags=re.IGNORECASE)
            assert (
                regex.groups > 1
            ), "Found formatter pattern to split that has a single group; this leads to recursion errors"
            return regex

        capitalizers = [
            BaseWordCapitalizer.from_string(p) for p in config.capitalize_terms
        ]
        splitter_patterns = [splitter_pattern(p) for p in config.patterns_to_split]
        snake_case_terms = config.snake_case_after_terms

        return cls(
            config.symbol_casing_settings,
            capitalizers,
            splitter_patterns,
            snake_case_terms,
        )

    def format(self, name: CompoundSymbolName, decl: CDeclKind) -> CompoundSymbolName:
        # Initial capitalization
        name = self.pre_capitalization(name, decl)

        # Split/capitalize
        components: list[CompoundSymbolName.Component] = []
        for split in (self.split_and_capitalize(c) for c in name.components):
            components.extend(split)

        if len(name.components) > 0:
            is_camel_case = name.components[0].to_string(False)[0].islower()

            if is_camel_case and len(components) > 0:
                components[0] = components[0].with_string_case(ComponentCase.LOWER)

        # Snake case
        components = self.snake_case(components)

        return CompoundSymbolName(components)

    def pre_capitalization(
        self,
        name: CompoundSymbolName,
        decl: CDeclKind,
    ) -> CompoundSymbolName:
        match decl:
            case CDeclKind.ENUM:
                return self._capitalize(name, self.symbol_case_settings.enums)
            case CDeclKind.ENUM_CASE:
                return self._capitalize(name, self.symbol_case_settings.enum_members)
            case CDeclKind.STRUCT:
                return self._capitalize(name, self.symbol_case_settings.structs)
            case CDeclKind.FUNC:
                return self._capitalize(name, self.symbol_case_settings.functions)
            case _:
                raise ValueError(f"Unknown C declaration kind {decl}")

    def _capitalize(
        self,
        name: CompoundSymbolName,
        capitalization: GeneratorConfig.Declarations.SymbolCasing,
    ):
        e = GeneratorConfig.Declarations.SymbolCasing
        match capitalization:
            case e.SNAKE_CASE:
                return name.lower_snake_cased()
            case e.PASCAL_CASE:
                return name.pascal_cased()
            case e.CAMEL_CASE:
                return name.camel_cased()
            case e.UPPER_SNAKE_CASE:
                return name.upper_snake_cased()
            case e.MIXED_CASE:
                return name.copy()
            case _:
                raise ValueError(f"Unknown symbol capitalization {capitalization}")

    def split_and_capitalize(
        self, component: CompoundSymbolName.Component
    ) -> list[CompoundSymbolName.Component]:
        # Split component
        split_string: list[str] = []
        self.split_component_inplace(component.string, split_string)

        # Capitalize
        split_components_str: list[Tuple[str, ComponentCase]] = []
        for c in (
            self.capitalize_component_string(p[1], has_prev=p[0] > 0)
            for p in enumerate(split_string)
        ):
            split_components_str.extend(c)

        # Rejoin and end
        return list(
            component.with_string(t[0]).with_string_case(component.string_case | t[1])
            for t in split_components_str
        )

    def split_component_inplace(self, string: str, output: list[str]):
        """Performs recursive in-place splitting of `string` along `self.words_to_split` boundaries into `output`."""

        for pattern in self.words_to_split:
            if not pattern.search(string):
                continue

            filtered = [
                x for x in pattern.split(string) if x is not None and len(x) > 0
            ]

            if len(filtered) == 1 and filtered[0] == string:
                break

            for word in filtered:
                self.split_component_inplace(word, output)

            return

        output.append(string)

    def split_component_string(self, string: str) -> list[str]:
        for pattern in self.words_to_split:
            if pattern.match(string):
                filtered = filter(lambda x: len(x) > 0, pattern.split(string))

                return list(filtered)

        return [string]

    def capitalize_component_string(
        self, string: str, has_prev: bool
    ) -> list[Tuple[str, ComponentCase]]:
        result: list[Tuple[str, ComponentCase]] = []
        leftmost_interval: Tuple[str, int, int] | None = None

        for capitalizer in self.capitalizers:
            cap_result = capitalizer.suggest_capitalization(
                string, has_leading_string=has_prev
            )
            if cap_result is None:
                continue

            if leftmost_interval is None or cap_result[1] < leftmost_interval[1]:
                leftmost_interval = cap_result

        if leftmost_interval is None:
            if has_prev:
                string = string[0].upper() + string[1:]

            return [(string, ComponentCase.ANY)]

        if leftmost_interval[1] > 0:
            result.extend(
                self.capitalize_component_string(
                    string[0 : leftmost_interval[1]], has_prev=has_prev
                )
            )

        result.append((leftmost_interval[0], ComponentCase.AS_IS))

        if leftmost_interval[2] < len(string) - 1:
            result.extend(
                self.capitalize_component_string(
                    string[leftmost_interval[2] :], has_prev=True
                )
            )

        return result

    def snake_case(
        self, components: list[CompoundSymbolName.Component]
    ) -> list[CompoundSymbolName.Component]:
        result = []
        snake_case_next = False

        for comp in components:
            if snake_case_next:
                comp = comp.with_joint_to_prev("_").lower()
                snake_case_next = False

            for term in self.terms_to_snake_case_after:
                if comp.string == term:
                    snake_case_next = True
                    break

            result.append(comp)

        return result
