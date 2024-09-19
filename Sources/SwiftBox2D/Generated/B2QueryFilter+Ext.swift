// HEADS UP!: Auto-generated file, changes made directly here will be overwritten by code generators.
// Generated by generate_types.py

import box2d

/// The query filter is used to filter collisions between queries and shapes. For example,
/// you may want a ray-cast representing a projectile to hit players and the static environment
/// but not debris.
///  shape
public typealias B2QueryFilter = b2QueryFilter

extension B2QueryFilter: @retroactive CustomStringConvertible, @retroactive Equatable, @retroactive Hashable { }

public extension B2QueryFilter {
    var description: String {
        "b2QueryFilter(categoryBits: \(categoryBits), maskBits: \(maskBits))"
    }
    
    static func == (_ lhs: Self, _ rhs: Self) -> Bool {
        lhs.categoryBits == rhs.categoryBits && lhs.maskBits == rhs.maskBits
    }
    
    func hash(into hasher: inout Hasher) {
        hasher.combine(categoryBits)
        hasher.combine(maskBits)
    }
}
