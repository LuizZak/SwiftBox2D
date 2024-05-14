// HEADS UP!: Auto-generated file, changes made directly here will be overwritten by code generators.
// Generated by generate_types.py

import box2d

public extension B2Joint {
    /// Joint identifier validation. Provides validation for up to 64K allocations.
    func isValid() -> Bool {
        b2Joint_IsValid(id)
    }
    
    /// Get the joint type
    func getType() -> b2JointType {
        b2Joint_GetType(id)
    }
    
    /// Get body A on a joint
    func getBodyA() -> b2BodyId {
        b2Joint_GetBodyA(id)
    }
    
    /// Get body B on a joint
    func getBodyB() -> b2BodyId {
        b2Joint_GetBodyB(id)
    }
    
    /// Get local anchor on bodyA
    func getLocalAnchorA() -> B2Vec2 {
        b2Joint_GetLocalAnchorA(id)
    }
    
    /// Get local anchor on bodyB
    func getLocalAnchorB() -> B2Vec2 {
        b2Joint_GetLocalAnchorB(id)
    }
    
    /// Toggle collision between connected bodies
    func setCollideConnected(_ shouldCollide: Bool) {
        b2Joint_SetCollideConnected(id, shouldCollide)
    }
    
    /// Is collision allowed between connected bodies?
    func getCollideConnected() -> Bool {
        b2Joint_GetCollideConnected(id)
    }
    
    /// Set the user data on a joint
    func setUserData(_ userData: UnsafeMutableRawPointer?) {
        b2Joint_SetUserData(id, userData)
    }
    
    /// Wake the bodies connect to this joint
    func wakeBodies() {
        b2Joint_WakeBodies(id)
    }
}
