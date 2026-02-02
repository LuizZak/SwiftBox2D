import box2d

extension b2ShapeDef {
    /// Use this to initialize your shape definition.
    public static func `default`() -> Self {
        return b2DefaultShapeDef()
    }
}
