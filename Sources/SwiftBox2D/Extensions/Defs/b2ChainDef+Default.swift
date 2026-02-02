import box2d

extension b2ChainDef {
    /// Use this to initialize your chain definition.
    public static func `default`() -> Self {
        return b2DefaultChainDef()
    }
}
