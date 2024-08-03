// swift-tools-version: 5.10
import PackageDescription

let package = Package(
    name: "SwiftBox2D",
    products: [
        .library(
            name: "SwiftBox2D",
            targets: ["SwiftBox2D"]
        ),
    ],
    targets: [
        .target(
            name: "box2d",
            cSettings: [
                .unsafeFlags(["-mavx2"]),
            ]
        ),
        .target(
            name: "SwiftBox2D",
            dependencies: ["box2d"]
        ),
        .testTarget(
            name: "SwiftBox2DTests",
            dependencies: ["SwiftBox2D"]
        ),
    ]
)
