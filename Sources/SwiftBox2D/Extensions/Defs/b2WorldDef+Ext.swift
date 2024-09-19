import box2d

extension b2WorldDef {
    /// Use this to initialize your world definition.
    static var `default`: Self {
        return b2DefaultWorldDef()
    }
}
