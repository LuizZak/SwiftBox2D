import box2d

/// A prismatic (slider) joint.
public class B2PrismaticJoint: B2Joint {

}

extension b2PrismaticJointDef {
    /// Use this to initialize your joint definition.
    public static var `default`: Self {
        b2DefaultPrismaticJointDef()
    }
}
