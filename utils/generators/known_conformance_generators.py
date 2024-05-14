from utils.generators.conformances.custom_string_conformance import (
    SwiftCustomStringConvertibleConformance,
)
from utils.generators.conformances.equatable_conformance import (
    SwiftEquatableConformance,
)
from utils.generators.conformances.hashable_conformance import SwiftHashableConformance
from utils.generators.swift_conformance_generator import SwiftConformanceGenerator


KNOWN_CONFORMANCES_GENERATORS: list[SwiftConformanceGenerator] = [
    SwiftHashableConformance(),
    SwiftEquatableConformance(),
    SwiftCustomStringConvertibleConformance(),
]


def get_conformance_generator(protocol: str) -> SwiftConformanceGenerator | None:
    for generator in KNOWN_CONFORMANCES_GENERATORS:
        if generator.protocol_name == protocol:
            return generator

    return None
