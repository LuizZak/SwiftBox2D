// HEADS UP!: Auto-generated file, changes made directly here will be overwritten by code generators.
// Generated by generate_types.py

import box2d

/// The body simulation type.
/// Each body is one of these three types. The type determines how the body behaves in the simulation.
///  body
public typealias B2BodyType = b2BodyType

public extension B2BodyType {
    /// zero mass, zero velocity, may be manually moved
    static let b2StaticBody = b2_staticBody
    
    /// zero mass, velocity set by user, moved by solver
    static let b2KinematicBody = b2_kinematicBody
    
    /// positive mass, velocity determined by forces, moved by solver
    static let b2DynamicBody = b2_dynamicBody
    
    /// number of body types
    static let b2BodyTypeCount = b2_bodyTypeCount
}
