import box2d

/// A mouse joint.
public class B2MouseJoint: B2Joint {

}

extension b2MouseJointDef {
    /// Use this to initialize your joint definition.
    public static var `default`: Self {
        b2DefaultMouseJointDef()
    }
}
