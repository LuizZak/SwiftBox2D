// HEADS UP!: Auto-generated file, changes made directly here will be overwritten by code generators.
// Generated by generate_types.py

import box2d

public extension B2WheelJoint {
    func enableSpring(_ enableSpring: Bool) {
        b2WheelJoint_EnableSpring(id, enableSpring)
    }
    
    func isSpringEnabled() -> Bool {
        b2WheelJoint_IsSpringEnabled(id)
    }
    
    /// Set the wheel joint stiffness in Hertz
    func setSpringHertz(_ hertz: Float) {
        b2WheelJoint_SetSpringHertz(id, hertz)
    }
    
    /// - returns: the wheel joint stiffness in Hertz
    func getSpringHertz() -> Float {
        b2WheelJoint_GetSpringHertz(id)
    }
    
    /// Set the wheel joint damping ratio (non-dimensional)
    func setSpringDampingRatio(_ dampingRatio: Float) {
        b2WheelJoint_SetSpringDampingRatio(id, dampingRatio)
    }
    
    /// - returns: the wheel joint damping ratio (non-dimensional)
    func getSpringDampingRatio() -> Float {
        b2WheelJoint_GetSpringDampingRatio(id)
    }
    
    /// Enable/disable the wheel joint limit.
    func enableLimit(_ enableLimit: Bool) {
        b2WheelJoint_EnableLimit(id, enableLimit)
    }
    
    /// - returns: is the wheel joint limit enabled
    func isLimitEnabled() -> Bool {
        b2WheelJoint_IsLimitEnabled(id)
    }
    
    /// Get the lower joint limit in length units (meters).
    func getLowerLimit() -> Float {
        b2WheelJoint_GetLowerLimit(id)
    }
    
    /// Get the upper joint limit in length units (meters).
    func getUpperLimit() -> Float {
        b2WheelJoint_GetUpperLimit(id)
    }
    
    /// Set the joint limits in length units (meters).
    func setLimits(_ lower: Float, _ upper: Float) {
        b2WheelJoint_SetLimits(id, lower, upper)
    }
    
    /// Enable/disable the wheel joint motor
    func enableMotor(_ enableMotor: Bool) {
        b2WheelJoint_EnableMotor(id, enableMotor)
    }
    
    /// - returns: is the wheel joint motor enabled
    func isMotorEnabled() -> Bool {
        b2WheelJoint_IsMotorEnabled(id)
    }
    
    /// Set the wheel joint motor speed in radians per second
    func setMotorSpeed(_ motorSpeed: Float) {
        b2WheelJoint_SetMotorSpeed(id, motorSpeed)
    }
    
    /// - returns: the wheel joint motor speed in radians per second
    func getMotorSpeed() -> Float {
        b2WheelJoint_GetMotorSpeed(id)
    }
    
    /// Get the wheel joint current motor torque
    func getMotorTorque() -> Float {
        b2WheelJoint_GetMotorTorque(id)
    }
    
    /// Set the wheel joint maximum motor torque
    func setMaxMotorTorque(_ torque: Float) {
        b2WheelJoint_SetMaxMotorTorque(id, torque)
    }
    
    /// - returns: the wheel joint maximum motor torque
    func getMaxMotorTorque() -> Float {
        b2WheelJoint_GetMaxMotorTorque(id)
    }
    
    /// Get the current wheel joint constraint force
    func getConstraintForce() -> b2Vec2 {
        b2WheelJoint_GetConstraintForce(id)
    }
    
    /// Get the current wheel joint constraint torque
    func getConstraintTorque() -> Float {
        b2WheelJoint_GetConstraintTorque(id)
    }
}