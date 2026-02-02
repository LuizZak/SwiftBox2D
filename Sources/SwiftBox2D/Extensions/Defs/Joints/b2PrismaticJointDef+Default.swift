import box2d

extension b2PrismaticJointDef {
    /// Use this to initialize your prismatic joint definition.
    public static func `default`() -> Self {
        return b2DefaultPrismaticJointDef()
    }
}
