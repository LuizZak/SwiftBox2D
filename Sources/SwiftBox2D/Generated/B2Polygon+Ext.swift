// HEADS UP!: Auto-generated file, changes made directly here will be overwritten by code generators.
// Generated by generate_types.py

import box2d

public typealias B2Polygon = b2Polygon

extension B2Polygon: @retroactive CustomStringConvertible { }

public extension B2Polygon {
    var description: String {
        "b2Polygon(vertices: \(vertices), normals: \(normals), centroid: \(centroid), radius: \(radius), count: \(count))"
    }
}
