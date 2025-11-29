import box2d

extension b2WorldDef {
    /// Use this to initialize your world definition.
    public static var `default`: Self {
        return b2DefaultWorldDef()
    }
}
