// HEADS UP!: Auto-generated file, changes made directly here will be overwritten by code generators.
// Generated by generate_types.py

import box2d

/// A 2D rigid transform
public typealias B2Transform = b2Transform

extension B2Transform: @retroactive CustomStringConvertible, @retroactive Equatable, @retroactive Hashable { }

public extension B2Transform {
    var description: String {
        "b2Transform(p: \(p), q: \(q))"
    }
    
    static func == (_ lhs: Self, _ rhs: Self) -> Bool {
        lhs.p == rhs.p && lhs.q == rhs.q
    }
    
    func hash(into hasher: inout Hasher) {
        hasher.combine(p)
        hasher.combine(q)
    }
}
