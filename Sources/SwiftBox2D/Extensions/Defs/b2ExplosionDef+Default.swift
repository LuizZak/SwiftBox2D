import box2d

extension b2ExplosionDef {
    /// Use this to initialize your explosion definition
    public static func `default`() -> Self {
        return b2DefaultExplosionDef()
    }
}
