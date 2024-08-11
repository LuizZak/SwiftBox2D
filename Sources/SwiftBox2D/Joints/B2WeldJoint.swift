import box2d

/// A weld joint.
public class B2WeldJoint: B2Joint {

}

extension b2WeldJointDef {
    /// Use this to initialize your joint definition.
    public static var `default`: Self {
        b2DefaultWeldJointDef()
    }
}
