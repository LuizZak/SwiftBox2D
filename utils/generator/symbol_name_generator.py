from utils.converters.default_symbol_name_formatter import DefaultSymbolNameFormatter
from utils.converters.symbol_name_formatter import SymbolNameFormatter
from utils.data.compound_symbol_name import CompoundSymbolName
from utils.data.generator_config import GeneratorConfig

class SymbolNameGenerator:
    formatter: SymbolNameFormatter
    symbolCasingSettings: GeneratorConfig.Declarations.SymbolCasingSettings

    def __init__(
        self,
        formatter: SymbolNameFormatter,
        symbolCasingSettings: GeneratorConfig.Declarations.SymbolCasingSettings
    ):
        self.formatter = formatter
        self.symbolCasingSettings = symbolCasingSettings
    
    @classmethod
    def from_config(cls, config: GeneratorConfig.Declarations):
        return cls(
            formatter=DefaultSymbolNameFormatter.from_config(config.formatter),
            symbolCasingSettings=config.symbolCasing
        )

    def generate_from_symbol_casing(
        self,
        name: str,
        casing: GeneratorConfig.Declarations.SymbolCasing
    ) -> CompoundSymbolName:
        return self.formatter.format(compound_symbol_with_casing(name, casing))

    def generate_enum_name(self, name: str) -> CompoundSymbolName:
        return self.generate_from_symbol_casing(name, self.symbolCasingSettings.enums)

    def generate_enum_case(
        self, enum_name: CompoundSymbolName, enum_original_name: str, case_name: str
    ) -> CompoundSymbolName:
        return self.generate_from_symbol_casing(case_name, self.symbolCasingSettings.enumMembers)

    def generate_struct_name(self, name: str) -> CompoundSymbolName:
        return self.generate_from_symbol_casing(name, self.symbolCasingSettings.structs)

    def generate_original_enum_name(self, name: str) -> CompoundSymbolName:
        return self.generate_from_symbol_casing(name, self.symbolCasingSettings.enums)

    def generate_original_enum_case(self, case_name: str) -> CompoundSymbolName:
        return self.generate_from_symbol_casing(case_name, self.symbolCasingSettings.enumMembers)
    
    def generate_funcDecl_name(self, name: str) -> CompoundSymbolName:
        return self.generate_from_symbol_casing(name, self.symbolCasingSettings.functions)

def compound_symbol_with_casing(
    name: str,
    casing: GeneratorConfig.Declarations.SymbolCasing
) -> CompoundSymbolName:
    e = GeneratorConfig.Declarations.SymbolCasing

    symbolName: CompoundSymbolName
    match casing:
        case e.SNAKE_CASE:
            symbolName = CompoundSymbolName.from_snake_case(name)
        case e.PASCAL_CASE:
            symbolName = CompoundSymbolName.from_pascal_case(name)
        case e.CAMEL_CASE:
            symbolName = CompoundSymbolName.from_camel_case(name)
        case _:
            raise ValueError(f"Unknown symbol casing {casing}")
    
    return symbolName
