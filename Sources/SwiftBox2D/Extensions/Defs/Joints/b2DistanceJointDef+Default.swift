import box2d

extension b2DistanceJointDef {
    /// Use this to initialize your distance joint definition.
    public static var `default`: Self {
        return b2DefaultDistanceJointDef()
    }
}
