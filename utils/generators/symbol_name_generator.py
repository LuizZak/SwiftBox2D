from utils.converters.symbol_name_formatter import SymbolNameFormatter
from utils.data.c_decl_kind import CDeclKind
from utils.data.compound_symbol_name import CompoundSymbolName
from utils.data.generator_config import GeneratorConfig


class SymbolNameGenerator:
    formatter: SymbolNameFormatter
    symbol_casting_settings: GeneratorConfig.Declarations.SymbolCasingSettings

    def __init__(
        self,
        formatter: SymbolNameFormatter,
        symbol_casting_settings: GeneratorConfig.Declarations.SymbolCasingSettings,
    ):
        self.formatter = formatter
        self.symbol_casting_settings = symbol_casting_settings

    @classmethod
    def from_config(cls, config: GeneratorConfig.Declarations):
        return cls(
            formatter=SymbolNameFormatter.from_config(config.formatter),
            symbol_casting_settings=config.symbol_casing_settings,
        )

    def generate_from_symbol_casing(
        self,
        name: str,
        casing: GeneratorConfig.Declarations.SymbolCasing,
        c_decl_kind: CDeclKind,
    ) -> CompoundSymbolName:
        return self.formatter.format(
            compound_symbol_with_casing(name, casing), c_decl_kind
        )

    def generate_enum_name(self, name: str) -> CompoundSymbolName:
        return self.generate_from_symbol_casing(
            name, self.symbol_casting_settings.enums, CDeclKind.ENUM
        )

    def generate_enum_case(
        self, enum_name: CompoundSymbolName, enum_original_name: str, case_name: str
    ) -> CompoundSymbolName:
        return self.generate_from_symbol_casing(
            case_name, self.symbol_casting_settings.enum_members, CDeclKind.ENUM_CASE
        )

    def generate_struct_name(self, name: str) -> CompoundSymbolName:
        return self.generate_from_symbol_casing(
            name, self.symbol_casting_settings.structs, CDeclKind.STRUCT
        )

    def generate_func_decl_name(self, name: str) -> CompoundSymbolName:
        return self.generate_from_symbol_casing(
            name, self.symbol_casting_settings.functions, CDeclKind.FUNC
        )


def compound_symbol_with_casing(
    name: str, casing: GeneratorConfig.Declarations.SymbolCasing
) -> CompoundSymbolName:
    e = GeneratorConfig.Declarations.SymbolCasing

    symbol_name: CompoundSymbolName
    match casing:
        case e.PASCAL_CASE:
            symbol_name = CompoundSymbolName.from_pascal_case(name)
        case e.CAMEL_CASE:
            symbol_name = CompoundSymbolName.from_camel_case(name)
        case e.SNAKE_CASE:
            symbol_name = CompoundSymbolName.from_snake_case(name)
        case e.UPPER_SNAKE_CASE:
            symbol_name = CompoundSymbolName.from_snake_case(name)
        case e.MIXED_CASE:
            symbol_name = CompoundSymbolName.from_mixed_case(name)
        case _:
            raise ValueError(f"Unknown symbol casing {casing}")

    return symbol_name
