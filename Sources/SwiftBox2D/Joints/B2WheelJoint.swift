import box2d

/// A wheel joint.
public class B2WheelJoint: B2Joint {

}

extension b2WheelJointDef {
    /// Use this to initialize your joint definition.
    public static var `default`: Self {
        b2DefaultWheelJointDef()
    }
}
