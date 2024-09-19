import box2d

extension b2WeldJointDef {
    /// Use this to initialize your weld joint definition.
    public static var `default`: Self {
        return b2DefaultWeldJointDef()
    }
}
