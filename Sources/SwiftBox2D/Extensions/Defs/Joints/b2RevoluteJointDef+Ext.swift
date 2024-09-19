import box2d

extension b2RevoluteJointDef {
    /// Use this to initialize your revolute joint definition.
    static var `default`: Self {
        return b2DefaultRevoluteJointDef()
    }
}
