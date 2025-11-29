import box2d

/// Base class for joint types.
public class B2Joint {
    /// Gets the ID of this joint.
    private(set) public var id: b2JointId

    init(id: b2JointId) {
        self.id = id
    }

    /// Destroys this joint, removing it from the world that owns it.
    public func destroy(wakeAttached: Bool) {
        b2DestroyJoint(id, wakeAttached)

        self.id = b2_nullJointId
    }
}
