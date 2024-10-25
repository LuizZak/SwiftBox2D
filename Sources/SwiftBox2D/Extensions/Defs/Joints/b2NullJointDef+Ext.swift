import box2d

extension b2NullJointDef {
    /// Use this to initialize your null joint definition.
    public static var `default`: Self {
        return b2DefaultNullJointDef()
    }
}
