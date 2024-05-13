// HEADS UP!: Auto-generated file, changes made directly here will be overwritten by code generators.
// Generated by generate_types.py

import box2d

/// Enable/disable the joint spring.
public extension B2PrismaticJoint {
    /// Enable/disable the joint spring.
    func enableSpring(_ enableSpring: Bool) {
        b2PrismaticJoint_EnableSpring(id, enableSpring)
    }
    
    func isSpringEnabled() -> Bool {
        b2PrismaticJoint_IsSpringEnabled(id)
    }
    
    /// Set the joint stiffness in Hertz
    func setSpringHertz(_ hertz: Float) {
        b2PrismaticJoint_SetSpringHertz(id, hertz)
    }
    
    /// - returns: the joint stiffness in Hertz
    func getSpringHertz() -> Float {
        b2PrismaticJoint_GetSpringHertz(id)
    }
    
    /// Set the joint damping ratio (non-dimensional)
    func setSpringDampingRatio(_ dampingRatio: Float) {
        b2PrismaticJoint_SetSpringDampingRatio(id, dampingRatio)
    }
    
    /// - returns: the joint damping ratio (non-dimensional)
    func getSpringDampingRatio() -> Float {
        b2PrismaticJoint_GetSpringDampingRatio(id)
    }
    
    /// Enable/disable a prismatic joint limit
    func enableLimit(_ enableLimit: Bool) {
        b2PrismaticJoint_EnableLimit(id, enableLimit)
    }
    
    /// - returns: is the prismatic joint limit enabled
    func isLimitEnabled() -> Bool {
        b2PrismaticJoint_IsLimitEnabled(id)
    }
    
    /// Get the lower joint limit in length units (meters).
    func getLowerLimit() -> Float {
        b2PrismaticJoint_GetLowerLimit(id)
    }
    
    /// Get the upper joint limit in length units (meters).
    func getUpperLimit() -> Float {
        b2PrismaticJoint_GetUpperLimit(id)
    }
    
    /// Set the joint limits in length units (meters).
    func setLimits(_ lower: Float, _ upper: Float) {
        b2PrismaticJoint_SetLimits(id, lower, upper)
    }
    
    /// Enable/disable a prismatic joint motor
    func enableMotor(_ enableMotor: Bool) {
        b2PrismaticJoint_EnableMotor(id, enableMotor)
    }
    
    /// - returns: is the prismatic joint motor enabled
    func isMotorEnabled() -> Bool {
        b2PrismaticJoint_IsMotorEnabled(id)
    }
    
    /// Set the motor speed for a prismatic joint
    func setMotorSpeed(_ motorSpeed: Float) {
        b2PrismaticJoint_SetMotorSpeed(id, motorSpeed)
    }
    
    /// - returns: the motor speed for a prismatic joint
    func getMotorSpeed() -> Float {
        b2PrismaticJoint_GetMotorSpeed(id)
    }
    
    /// Get the current motor force for a prismatic joint
    func getMotorForce() -> Float {
        b2PrismaticJoint_GetMotorForce(id)
    }
    
    /// Set the maximum force for a prismatic joint motor
    func setMaxMotorForce(_ force: Float) {
        b2PrismaticJoint_SetMaxMotorForce(id, force)
    }
    
    /// - returns: the maximum force for a prismatic joint motor
    func getMaxMotorForce() -> Float {
        b2PrismaticJoint_GetMaxMotorForce(id)
    }
    
    /// Get the current constraint force for a prismatic joint
    func getConstraintForce() -> b2Vec2 {
        b2PrismaticJoint_GetConstraintForce(id)
    }
    
    /// Get the current constraint torque for a prismatic joint
    func getConstraintTorque() -> Float {
        b2PrismaticJoint_GetConstraintTorque(id)
    }
}
