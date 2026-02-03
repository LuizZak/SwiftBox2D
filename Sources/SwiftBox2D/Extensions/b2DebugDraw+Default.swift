import box2d

extension b2DebugDraw {
    /// Use this to initialize your drawing interface. This allows you to
    /// implement a sub-set of the drawing functions.
    @inlinable
    public static func `default`() -> Self {
        b2DefaultDebugDraw()
    }
}
