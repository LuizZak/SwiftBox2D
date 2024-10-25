// HEADS UP!: Auto-generated file, changes made directly here will be overwritten by code generators.
// Generated by generate_types.py

import box2d

public extension B2WeldJoint {
    /// Get the weld joint reference angle in radians
    /// Set the weld joint reference angle in radians, must be in [-pi,pi].
    var referenceAngle: Float {
        get {
            b2WeldJoint_GetReferenceAngle(id)
        }
        set(angleInRadians) {
            b2WeldJoint_SetReferenceAngle(id, angleInRadians)
        }
    }
    
    /// Get the weld joint linear stiffness in Hertz
    /// Set the weld joint linear stiffness in Hertz. 0 is rigid.
    var linearHertz: Float {
        get {
            b2WeldJoint_GetLinearHertz(id)
        }
        set(hertz) {
            b2WeldJoint_SetLinearHertz(id, hertz)
        }
    }
    
    /// Get the weld joint linear damping ratio (non-dimensional)
    /// Set the weld joint linear damping ratio (non-dimensional)
    var linearDampingRatio: Float {
        get {
            b2WeldJoint_GetLinearDampingRatio(id)
        }
        set(dampingRatio) {
            b2WeldJoint_SetLinearDampingRatio(id, dampingRatio)
        }
    }
    
    /// Get the weld joint angular stiffness in Hertz
    /// Set the weld joint angular stiffness in Hertz. 0 is rigid.
    var angularHertz: Float {
        get {
            b2WeldJoint_GetAngularHertz(id)
        }
        set(hertz) {
            b2WeldJoint_SetAngularHertz(id, hertz)
        }
    }
    
    /// Get the weld joint angular damping ratio, non-dimensional
    /// Set weld joint angular damping ratio, non-dimensional
    var angularDampingRatio: Float {
        get {
            b2WeldJoint_GetAngularDampingRatio(id)
        }
        set(dampingRatio) {
            b2WeldJoint_SetAngularDampingRatio(id, dampingRatio)
        }
    }
}
