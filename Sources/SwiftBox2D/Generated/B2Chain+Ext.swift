// HEADS UP!: Auto-generated file, changes made directly here will be overwritten by code generators.
// Generated by generate_types.py

import box2d

public extension B2Chain {
    /// Get the world that owns this chain shape
    func getWorld() -> b2WorldId {
        b2Chain_GetWorld(id)
    }
    
    /// Get the number of segments on this chain
    func getSegmentCount() -> Int32 {
        b2Chain_GetSegmentCount(id)
    }
    
    /// Fill a user array with chain segment shape ids up to the specified capacity. Returns
    /// the actual number of segments returned.
    func getSegments(_ segmentArray: UnsafeMutablePointer<b2ShapeId>?, _ capacity: Int32) -> Int32 {
        b2Chain_GetSegments(id, segmentArray, capacity)
    }
    
    /// Set the chain friction
    /// @see b2ChainDef::friction
    func setFriction(_ friction: Float) {
        b2Chain_SetFriction(id, friction)
    }
    
    /// Set the chain restitution (bounciness)
    /// @see b2ChainDef::restitution
    func setRestitution(_ restitution: Float) {
        b2Chain_SetRestitution(id, restitution)
    }
    
    /// Chain identifier validation. Provides validation for up to 64K allocations.
    func isValid() -> Bool {
        b2Chain_IsValid(id)
    }
}
