from utils.data.compound_symbol_name import CompoundSymbolName
from utils.data.c_decl_kind import CDeclKind


class SymbolNameFormatter:
    def format(self, name: CompoundSymbolName, decl: CDeclKind) -> CompoundSymbolName:
        return name
