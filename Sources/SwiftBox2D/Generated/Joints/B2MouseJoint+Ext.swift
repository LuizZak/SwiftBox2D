// HEADS UP!: Auto-generated file, changes made directly here will be overwritten by code generators.
// Generated by generate_types.py

import box2d

/// Set the target for a mouse joint
public extension B2MouseJoint {
    /// Set the target for a mouse joint
    func setTarget(_ target: b2Vec2) {
        b2MouseJoint_SetTarget(id, target)
    }
    
    /// @return the target for a mouse joint
    func getTarget() -> b2Vec2 {
        b2MouseJoint_GetTarget(id)
    }
    
    /// Set the spring stiffness in Hertz
    func setSpringHertz(_ hertz: Float) {
        b2MouseJoint_SetSpringHertz(id, hertz)
    }
    
    /// Set the spring damping ratio (non-dimensional)
    func setSpringDampingRatio(_ dampingRatio: Float) {
        b2MouseJoint_SetSpringDampingRatio(id, dampingRatio)
    }
    
    /// Get the Hertz of a mouse joint
    func getHertz() -> Float {
        b2MouseJoint_GetHertz(id)
    }
    
    /// Get the damping ratio of a mouse joint
    func getDampingRatio() -> Float {
        b2MouseJoint_GetDampingRatio(id)
    }
}
