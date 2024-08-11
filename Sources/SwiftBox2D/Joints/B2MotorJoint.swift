import box2d

/// A motor joint.
public class B2MotorJoint: B2Joint {

}

extension b2MotorJointDef {
    /// Use this to initialize your joint definition.
    public static var `default`: Self {
        b2DefaultMotorJointDef()
    }
}
