import box2d

extension b2Vec2 {
    @inlinable
    public static var zero: Self {
        b2Vec2_zero
    }
    
    /// Component-wise minimum vector
    @inlinable
    public static func min(_ a: Self, _ b: Self) -> Self {
        return b2Min(a, b)
    }
    
    /// Component-wise maximum vector
    @inlinable
    public static func max(_ a: Self, _ b: Self) -> Self {
        return b2Max(a, b)
    }
    
    /// Component-wise clamp vector v into the range [a, b]
    @inlinable
    public static func clamp(_ value: Self, min a: Self, max b: Self) -> Self {
        return b2Clamp(value, a, b)
    }
}

extension b2Vec2 {
    @inlinable
    public static prefix func - (value: Self) -> Self {
        return b2Neg(value)
    }
    
    @inlinable
    public static func + (lhs: Self, rhs: Self) -> Self {
        b2Add(lhs, rhs)
    }

    @inlinable
    public static func - (lhs: Self, rhs: Self) -> Self {
        b2Sub(lhs, rhs)
    }

    @inlinable
    public static func * (lhs: Self, rhs: Self) -> Self {
        b2Mul(lhs, rhs)
    }

    @inlinable
    public static func / (lhs: Self, rhs: Self) -> Self {
        binaryOp(lhs, rhs, /)
    }

    // MARK: Scalars

    @inlinable
    public static func + (lhs: Self, rhs: Float) -> Self {
        binaryOp(lhs, rhs, +)
    }

    @inlinable
    public static func + (lhs: Float, rhs: Self) -> Self {
        binaryOp(lhs, rhs, +)
    }

    @inlinable
    public static func - (lhs: Self, rhs: Float) -> Self {
        binaryOp(lhs, rhs, -)
    }

    @inlinable
    public static func - (lhs: Float, rhs: Self) -> Self {
        binaryOp(lhs, rhs, -)
    }

    @inlinable
    public static func * (lhs: Self, rhs: Float) -> Self {
        binaryOp(lhs, rhs, *)
    }

    @inlinable
    public static func * (lhs: Float, rhs: Self) -> Self {
        binaryOp(lhs, rhs, *)
    }

    @inlinable
    public static func / (lhs: Self, rhs: Float) -> Self {
        binaryOp(lhs, rhs, /)
    }

    @inlinable
    public static func / (lhs: Float, rhs: Self) -> Self {
        binaryOp(lhs, rhs, /)
    }

    // MARK: Internal

    @inlinable
    static func binaryOp(_ lhs: Self, _ rhs: Self, _ op: (Float, Float) -> Float) -> Self {
        .init(x: op(lhs.x, rhs.x), y: op(lhs.y, rhs.y))
    }

    @inlinable
    static func binaryOp(_ lhs: Float, _ rhs: Self, _ op: (Float, Float) -> Float) -> Self {
        .init(x: op(lhs, rhs.x), y: op(lhs, rhs.y))
    }

    @inlinable
    static func binaryOp(_ lhs: Self, _ rhs: Float, _ op: (Float, Float) -> Float) -> Self {
        .init(x: op(lhs.x, rhs), y: op(lhs.y, rhs))
    }
}
