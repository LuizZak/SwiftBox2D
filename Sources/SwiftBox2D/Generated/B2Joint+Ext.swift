// HEADS UP!: Auto-generated file, changes made directly here will be overwritten by code generators.
// Generated by generate_types.py

import box2d

public extension B2Joint {
    /// Joint identifier validation. Provides validation for up to 64K allocations.
    func isValid() -> Bool {
        b2Joint_IsValid(id)
    }
    
    /// Get the joint type
    func getType() -> B2JointType {
        b2Joint_GetType(id)
    }
    
    /// Get body A id on a joint
    func getBodyA() -> b2BodyId {
        b2Joint_GetBodyA(id)
    }
    
    /// Get body B id on a joint
    func getBodyB() -> b2BodyId {
        b2Joint_GetBodyB(id)
    }
    
    /// Get the world that owns this joint
    func getWorld() -> b2WorldId {
        b2Joint_GetWorld(id)
    }
    
    /// Get the local anchor on bodyA
    func getLocalAnchorA() -> B2Vec2 {
        b2Joint_GetLocalAnchorA(id)
    }
    
    /// Get the local anchor on bodyB
    func getLocalAnchorB() -> B2Vec2 {
        b2Joint_GetLocalAnchorB(id)
    }
    
    /// Set the user data on a joint
    func setUserData(_ userData: UnsafeMutableRawPointer?) {
        b2Joint_SetUserData(id, userData)
    }
    
    /// Wake the bodies connect to this joint
    func wakeBodies() {
        b2Joint_WakeBodies(id)
    }
    
    /// Get the current constraint force for this joint. Usually in Newtons.
    func getConstraintForce() -> B2Vec2 {
        b2Joint_GetConstraintForce(id)
    }
    
    /// Get the current constraint torque for this joint. Usually in Newton * meters.
    func getConstraintTorque() -> Float {
        b2Joint_GetConstraintTorque(id)
    }
    
    /// Is collision allowed between connected bodies?
    /// Toggle collision between connected bodies
    var collideConnected: Bool {
        get {
            b2Joint_GetCollideConnected(id)
        }
        set(shouldCollide) {
            b2Joint_SetCollideConnected(id, shouldCollide)
        }
    }
}
