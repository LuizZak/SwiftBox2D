from dataclasses import dataclass
import json


@dataclass
class GeneratorConfig:
    fileGeneration: "FileGeneration"
    declarations: "Declarations"
    formatter: "NameFormatter | None"
    docComments: "DocComments | None"

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
            formatter=cls.NameFormatter.from_json(json["symbolFormatting"]),
            docComments=cls.DocComments.from_json(json["docComments"])
        )

    @dataclass
    class Declarations:
        prefixes: list[str]
        functionsToMethods: list["FunctionToMethodMapper"]
        structConformances: list["StructConformanceEntry"]
        filters: "Filters"

        @classmethod
        def from_json(cls, json: dict):
            return cls(
                prefixes=json["prefixes"],
                structConformances=list(map(lambda v: cls.StructConformanceEntry.from_json(v), json["structConformances"])) if json["structConformances"] is not None else [],
                functionsToMethods=list(map(lambda v: cls.FunctionToMethodMapper.from_json(v), json["functionsToMethods"])) if json["functionsToMethods"] is not None else [],
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
            param0: tuple[str, str]

            @classmethod
            def from_json(cls, json: dict):
                return cls(json["cPrefix"], json["swiftType"], (json["param0"]["swiftName"], json["param0"]["type"]))
        
        @dataclass
        class StructConformanceEntry:
            cName: str
            conformances: list[str]

            @classmethod
            def from_json(cls, json: dict):
                return cls(json["cName"], json["conformances"])
        
    @dataclass
    class DocComments:
        collect: bool
        
        @classmethod
        def from_json(cls, json: dict):
            return cls(json["collect"])
    
    @dataclass
    class NameFormatter:
        capitalizeTerms: list[str]
        patternsToSplit: list[str]
        snakeCaseAfterTerms: list[str]

        @classmethod
        def from_json(cls, json: dict):
            return cls(json["capitalizeTerms"], json["patternsToSplit"], json["snakeCaseAfterTerms"])
    
    @dataclass
    class FileGeneration:
        targetPath: str
        globalFileSuffix: str
        imports: list[str]
        
        @classmethod
        def from_json(cls, json: dict):
            return cls(json["targetPath"], json["globalFileSuffix"], json["imports"])


if __name__ == "__main__":
    testJson = """
    {
        "declarations": {
            "prefixes": ["b2"],
            "functionsToMethods": [
                { "cPrefix": "b2World_", "swiftType": "B2World", "param0": { "swiftName": "id", "type": "b2WorldId" } },
                { "cPrefix": "b2Body_", "swiftType": "B2Body", "param0": { "swiftName": "id", "type": "b2BodyId" } },
                { "cPrefix": "b2Joint_", "swiftType": "B2Joint", "param0": { "swiftName": "id", "type": "b2JointId" } },
                { "cPrefix": "b2Shape_", "swiftType": "B2Shape", "param0": { "swiftName": "id", "type": "b2ShapeId" } },
                { "cPrefix": "b2Chain_", "swiftType": "B2Chain", "param0": { "swiftName": "id", "type": "b2ChainId" } }
            ],
            "structConformances": [
                { "cName": "b2Vec2", "conformances": ["Equatable", "Hashable", "CustomStringConvertible"] },
                { "cName": "b2Circle", "conformances": ["Equatable", "Hashable"] }
            ],
            "filters": {
                "enums": [],
                "enumMembers": [],
                "structs": [],
                "methods": ["\\."]
            }
        },
        "symbolFormatting": {
            "capitalizeTerms": ["AABB"],
            "patternsToSplit": [],
            "snakeCaseAfterTerms": []
        },
        "docComments": {
            "collect": true
        },
        "fileGeneration": {
            "targetPath": "Sources/SwiftBox2D/Generated",
            "globalFileSuffix": "+Ext",
            "imports": []
        }
    }
    """

    config = GeneratorConfig.from_json(json.loads(testJson))
    print(config)
