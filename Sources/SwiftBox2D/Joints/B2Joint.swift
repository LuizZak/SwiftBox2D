import box2d

/// Base class for joint types.
public class B2Joint {
    /// Gets the ID of this joint.
    private(set) public var id: b2JointId

    /// Instantiates a generic `B2Joint` from an ID.
    public init(id: b2JointId) {
        self.id = id
    }

    /// Destroys this joint, removing it from the world that owns it.
    public func destroy(wakeAttached: Bool) {
        b2DestroyJoint(id, wakeAttached)

        self.id = b2_nullJointId
    }
    
    /// Gets the local attachment point on body A, transformed to world coordinates.
    public func worldPointA() -> B2Vec2 {
        precondition(id != b2_nullJointId, "Cannot access destroyed joint")
        
        let bodyA = B2Body(id: getBodyA())
        
        let transform = localFrameA * bodyA.getTransform()
        
        return transform * B2Vec2.zero
    }
    
    /// Gets the local attachment point on body B, transformed to world coordinates.
    public func worldPointB() -> B2Vec2 {
        precondition(id != b2_nullJointId, "Cannot access destroyed joint")
        
        let bodyB = B2Body(id: getBodyB())
        
        let transform = localFrameB * bodyB.getTransform()
        
        return transform * B2Vec2.zero
    }
}
