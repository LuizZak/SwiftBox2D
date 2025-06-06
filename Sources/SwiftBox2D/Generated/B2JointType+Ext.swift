// HEADS UP!: Auto-generated file, changes made directly here will be overwritten by code generators.
// Generated by generate_types.py

import box2d

/// Joint type enumeration
/// 
/// This is useful because all joint types use b2JointId and sometimes you
/// want to get the type of a joint.
///  joint
public typealias B2JointType = b2JointType

public extension B2JointType {
    static let b2DistanceJoint = b2_distanceJoint
    
    static let b2FilterJoint = b2_filterJoint
    
    static let b2MotorJoint = b2_motorJoint
    
    static let b2MouseJoint = b2_mouseJoint
    
    static let b2PrismaticJoint = b2_prismaticJoint
    
    static let b2RevoluteJoint = b2_revoluteJoint
    
    static let b2WeldJoint = b2_weldJoint
    
    static let b2WheelJoint = b2_wheelJoint
}
