import box2d

/// A revolute (hinge) joint.
public class B2RevoluteJoint: B2Joint {

}

extension b2RevoluteJointDef {
    /// Use this to initialize your joint definition.
    public static var `default`: Self {
        b2DefaultRevoluteJointDef()
    }
}
