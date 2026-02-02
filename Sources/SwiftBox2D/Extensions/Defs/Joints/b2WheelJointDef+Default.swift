import box2d

extension b2WheelJointDef {
    /// Use this to initialize your wheel joint definition.
    public static func `default`() -> Self {
        return b2DefaultWheelJointDef()
    }
}
