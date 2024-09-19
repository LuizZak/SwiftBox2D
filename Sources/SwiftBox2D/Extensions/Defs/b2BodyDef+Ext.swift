import box2d

extension b2BodyDef {
    /// Use this to initialize your body definition.
    public static var `default`: Self {
        return b2DefaultBodyDef()
    }
}
