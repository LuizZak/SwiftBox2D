import box2d

extension b2ShapeDef {
    /// Use this to initialize your shape definition.
    static var `default`: Self {
        return b2DefaultShapeDef()
    }
}
