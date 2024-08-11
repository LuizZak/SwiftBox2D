import box2d

/// A distance joint.
public class B2DistanceJoint: B2Joint {

}

extension b2DistanceJointDef {
    /// Use this to initialize your joint definition.
    public static var `default`: Self {
        b2DefaultDistanceJointDef()
    }
}
