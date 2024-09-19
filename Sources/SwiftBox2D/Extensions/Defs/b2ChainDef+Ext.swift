import box2d

extension b2ChainDef {
    /// Use this to initialize your chain definition.
    static var `default`: Self {
        return b2DefaultChainDef()
    }
}
