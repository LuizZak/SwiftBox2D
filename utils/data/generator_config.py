from dataclasses import dataclass
from enum import Enum
import json


@dataclass
class GeneratorConfig:
    fileGeneration: "FileGeneration"
    declarations: "Declarations"
    docComments: "DocComments"

    @classmethod
    def from_json_file(cls, filePath):
        with open(filePath) as file:
            return cls.from_json(json.load(file))
    
    @classmethod
    def from_json_string(cls, string):
        return cls.from_json(json.loads(string))

    @classmethod
    def from_json(cls, json: dict):
        return GeneratorConfig(
            fileGeneration=cls.FileGeneration.from_json(json["fileGeneration"]),
            declarations=cls.Declarations.from_json(json["declarations"]),
            docComments=cls.DocComments.from_json(json["docComments"])
        )

    @dataclass
    class Declarations:
        class SymbolCasing(Enum):
            CAMEL_CASE="camelCase"
            PASCAL_CASE="pascalCase"
            SNAKE_CASE="snakeCase"
        
        @dataclass
        class SymbolCasingSettings:
            enums: "GeneratorConfig.Declarations.SymbolCasing"
            enumMembers: "GeneratorConfig.Declarations.SymbolCasing"
            structs: "GeneratorConfig.Declarations.SymbolCasing"
            functions: "GeneratorConfig.Declarations.SymbolCasing"

            @classmethod
            def from_json(cls, json: dict):
                return cls(
                    enums=GeneratorConfig.Declarations.SymbolCasing(json["enums"]),
                    enumMembers=GeneratorConfig.Declarations.SymbolCasing(json["enumMembers"]),
                    structs=GeneratorConfig.Declarations.SymbolCasing(json["structs"]),
                    functions=GeneratorConfig.Declarations.SymbolCasing(json["functions"]),
                )

        @dataclass
        class NameFormatter:
            symbolCasing: "GeneratorConfig.Declarations.SymbolCasing"
            capitalizeTerms: list[str]
            patternsToSplit: list[str]
            snakeCaseAfterTerms: list[str]

            @classmethod
            def from_json(cls, json: dict):
                return cls(
                    GeneratorConfig.Declarations.SymbolCasing(json["symbolCasing"]),
                    json["capitalizeTerms"],
                    json["patternsToSplit"],
                    json["snakeCaseAfterTerms"]
                )
        
        prefixes: list[str]
        symbolCasing: SymbolCasingSettings
        functionsToMethods: list["FunctionToMethodMapper"]
        conformances: list["ConformanceEntry"]
        formatter: "NameFormatter"
        filters: "Filters"

        @classmethod
        def from_json(cls, json: dict):
            return cls(
                prefixes=json["prefixes"],
                symbolCasing=cls.SymbolCasingSettings.from_json(json["symbolCasing"]),
                conformances=list(map(lambda v: cls.ConformanceEntry.from_json(v), json["conformances"])) if json["conformances"] is not None else [],
                functionsToMethods=list(map(lambda v: cls.FunctionToMethodMapper.from_json(v), json["functionsToMethods"])) if json["functionsToMethods"] is not None else [],
                formatter=cls.NameFormatter.from_json(json["swiftSymbolFormatting"]),
                filters=cls.Filters.from_json(json["filters"])
            )
        
        @dataclass
        class Filters:
            enums: list[str]
            enumMembers: list[str]
            structs: list[str]
            methods: list[str]

            @classmethod
            def from_json(cls, json: dict):
                return cls(
                    enums=json["enums"],
                    enumMembers=json["enumMembers"],
                    structs=json["structs"],
                    methods=json["methods"],
                )
        
        @dataclass
        class FunctionToMethodMapper:
            cPrefix: str
            swiftType: str
            accessLevel: str
            param0: tuple[str, str]

            @classmethod
            def from_json(cls, json: dict):
                return cls(
                    cPrefix=json["cPrefix"],
                    swiftType=json["swiftType"],
                    accessLevel=json.get("accessLevel", "public"),
                    param0=(json["param0"]["swiftName"], json["param0"]["type"])
                )
        
        @dataclass
        class ConformanceEntry:
            cName: str
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
                return cls(
                    path=json["path"],
                    patterns=json["match"]
                )

        targetPath: str
        globalFileSuffix: str
        imports: list[str]
        directoryStructure: list[DirectoryStructureEntry]
        
        @classmethod
        def from_json(cls, json: dict):
            directoryStructure = list(map(cls.DirectoryStructureEntry.from_json, json.get("directoryStructure", [])))

            return cls(
                targetPath=json["targetPath"],
                globalFileSuffix=json["globalFileSuffix"],
                imports=json["imports"],
                directoryStructure=directoryStructure
            )


if __name__ == "__main__":
    testJson = """
    {
        "declarations": {
            "prefixes": ["b2"],
            "symbolCasing": {
                "enums": "camelCase",
                "enumMembers": "snakeCase",
                "structs": "camelCase",
                "functions": "camelCase"
            },
            "swiftSymbolFormatting": {
                "symbolCasing": "camelCase",
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
