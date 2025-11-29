import box2d

extension b2MouseJointDef {
    /// Use this to initialize your mouse joint definition.
    public static var `default`: Self {
        return b2DefaultMouseJointDef()
    }
}
