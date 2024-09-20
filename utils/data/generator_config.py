from dataclasses import dataclass
from enum import Enum
import json
from os import PathLike


@dataclass
class GeneratorConfig:
    file_generation: "FileGeneration"
    declarations: "Declarations"
    doc_comments: "DocComments"

    @classmethod
    def from_json_file(cls, file_path: PathLike):
        with open(file_path) as file:
            return cls.from_json(json.load(file))

    @classmethod
    def from_json_string(cls, string: str | bytes | bytearray):
        return cls.from_json(json.loads(string))

    @classmethod
    def from_json(cls, json: dict):
        return GeneratorConfig(
            file_generation=cls.FileGeneration.from_json(json["fileGeneration"]),
            declarations=cls.Declarations.from_json(json["declarations"]),
            doc_comments=cls.DocComments.from_json(json["docComments"]),
        )

    @dataclass
    class Declarations:
        class SymbolCasing(Enum):
            CAMEL_CASE = "camelCase"
            PASCAL_CASE = "PascalCase"
            SNAKE_CASE = "snake_case"
            UPPER_SNAKE_CASE = "UPPER_SNAKE_CASE"
            MIXED_CASE = "mixed_Case"

        @dataclass
        class SymbolCasingSettings:
            enums: "GeneratorConfig.Declarations.SymbolCasing"
            enum_members: "GeneratorConfig.Declarations.SymbolCasing"
            structs: "GeneratorConfig.Declarations.SymbolCasing"
            functions: "GeneratorConfig.Declarations.SymbolCasing"

            @classmethod
            def from_json(cls, json: dict):
                return cls(
                    enums=GeneratorConfig.Declarations.SymbolCasing(json["enums"]),
                    enum_members=GeneratorConfig.Declarations.SymbolCasing(
                        json["enumMembers"]
                    ),
                    structs=GeneratorConfig.Declarations.SymbolCasing(json["structs"]),
                    functions=GeneratorConfig.Declarations.SymbolCasing(
                        json["functions"]
                    ),
                )

        @dataclass
        class SwiftNameFormatting:
            symbol_casing_settings: "GeneratorConfig.Declarations.SymbolCasingSettings"
            capitalize_terms: list[str]
            patterns_to_split: list[str]
            snake_case_after_terms: list[str]

            @classmethod
            def from_json(cls, json: dict):
                return cls(
                    GeneratorConfig.Declarations.SymbolCasingSettings.from_json(
                        json["symbolCasing"]
                    ),
                    json["capitalizeTerms"],
                    json["patternsToSplit"],
                    json["snakeCaseAfterTerms"],
                )

        prefixes: list[str]
        symbol_casing_settings: SymbolCasingSettings
        auto_property: bool
        functions_to_methods: list["FunctionToMethodMapper"]
        conformances: list["ConformanceEntry"]
        formatter: "SwiftNameFormatting"
        filters: "Filters"

        @classmethod
        def from_json(cls, json: dict):
            return cls(
                prefixes=json["prefixes"],
                symbol_casing_settings=cls.SymbolCasingSettings.from_json(
                    json["symbolCasing"]
                ),
                conformances=(
                    list(
                        map(
                            lambda v: cls.ConformanceEntry.from_json(v),
                            json["conformances"],
                        )
                    )
                    if json["conformances"] is not None
                    else []
                ),
                auto_property=json.get("autoProperty", False) == True,
                functions_to_methods=(
                    list(
                        map(
                            lambda v: cls.FunctionToMethodMapper.from_json(v),
                            json["functionsToMethods"],
                        )
                    )
                    if json["functionsToMethods"] is not None
                    else []
                ),
                formatter=cls.SwiftNameFormatting.from_json(
                    json["swiftSymbolFormatting"]
                ),
                filters=cls.Filters.from_json(json["filters"]),
            )

        @dataclass
        class Filters:
            enums: list[str]
            enum_members: list[str]
            structs: list[str]
            methods: list[str]

            @classmethod
            def from_json(cls, json: dict):
                return cls(
                    enums=json["enums"],
                    enum_members=json["enumMembers"],
                    structs=json["structs"],
                    methods=json["methods"],
                )

        @dataclass
        class FunctionToMethodMapper:
            c_prefix: str
            swift_type: str
            access_level: str
            param0: tuple[str, str]

            @classmethod
            def from_json(cls, json: dict):
                return cls(
                    c_prefix=json["cPrefix"],
                    swift_type=json["swiftType"],
                    access_level=json.get("accessLevel", "public"),
                    param0=(json["param0"]["swiftName"], json["param0"]["type"]),
                )

        @dataclass
        class ConformanceEntry:
            c_name: str
            conformances: list[str]

            @classmethod
            def from_json(cls, json: dict):
                return cls(json["cName"], json["conformances"])

    @dataclass
    class DocComments:
        collect: bool
        format: bool

        @classmethod
        def from_json(cls, json: dict):
            return cls(json["collect"], json["format"])

    @dataclass
    class FileGeneration:
        @dataclass
        class DirectoryStructureEntry:
            path: str
            patterns: list[str]

            @classmethod
            def from_json(cls, json: dict):
                return cls(path=json["path"], patterns=json["match"])

        target_path: str
        global_file_suffix: str
        imports: list[str]
        directory_structure: list[DirectoryStructureEntry]

        @classmethod
        def from_json(cls, json: dict):
            directory_structure = list(
                map(
                    cls.DirectoryStructureEntry.from_json,
                    json.get("directoryStructure", []),
                )
            )

            return cls(
                target_path=json["targetPath"],
                global_file_suffix=json["globalFileSuffix"],
                imports=json["imports"],
                directory_structure=directory_structure,
            )


if __name__ == "__main__":
    testJson = """
    {
        "declarations": {
            "prefixes": ["b2"],
            "symbolCasing": {
                "enums": "camelCase",
                "enumMembers": "UPPER_SNAKE_CASE",
                "structs": "camelCase",
                "functions": "camelCase"
            },
            "swiftSymbolFormatting": {
                "symbolCasing": {
                    "enums": "PascalCase",
                    "enumMembers": "UPPER_SNAKE_CASE",
                    "structs": "PascalCase",
                    "functions": "camelCase"
                },
                "capitalizeTerms": ["AABB"],
                "patternsToSplit": [],
                "snakeCaseAfterTerms": []
            },
            "functionsToMethods": [
                { "cPrefix": "b2World_", "swiftType": "B2World", "param0": { "swiftName": "id", "type": "b2WorldId" } },
                { "cPrefix": "b2Body_", "swiftType": "B2Body", "param0": { "swiftName": "id", "type": "b2BodyId" } },
                { "cPrefix": "b2Joint_", "swiftType": "B2Joint", "param0": { "swiftName": "id", "type": "b2JointId" } },
                { "cPrefix": "b2Shape_", "swiftType": "B2Shape", "param0": { "swiftName": "id", "type": "b2ShapeId" }, "accessLevel": "internal" },
                { "cPrefix": "b2Chain_", "swiftType": "B2Chain", "param0": { "swiftName": "id", "type": "b2ChainId" } }
            ],
            "conformances": [
                { "cName": "b2Vec2", "conformances": ["Equatable", "Hashable", "CustomStringConvertible"] },
                { "cName": "b2Circle", "conformances": ["Equatable", "Hashable"] }
            ],
            "filters": {
                "enums": [],
                "enumMembers": [],
                "structs": [],
                "methods": ["."]
            }
        },
        "docComments": {
            "collect": true,
            "format": true
        },
        "fileGeneration": {
            "targetPath": "Sources/SwiftBox2D/Generated",
            "globalFileSuffix": "+Ext",
            "imports": [],
            "directoryStructure": [
                { "path": "Folder", "match": ["/^SomePrefix.+/", "AFileName.swift"] }
            ]
        }
    }
    """
    config = GeneratorConfig.from_json(json.loads(testJson))
    print(config)
