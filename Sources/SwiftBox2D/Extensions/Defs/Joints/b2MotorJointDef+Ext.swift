import box2d

extension b2MotorJointDef {
    /// Use this to initialize your motor joint definition.
    public static var `default`: Self {
        return b2DefaultMotorJointDef()
    }
}
