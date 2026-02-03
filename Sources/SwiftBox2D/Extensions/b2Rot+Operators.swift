import box2d

extension B2Rot {
    /// Multiply two rotations: q * r
    @inlinable
    public static func * (lhs: Self, rhs: Self) -> Self {
        return b2MulRot(lhs, rhs)
    }
}
