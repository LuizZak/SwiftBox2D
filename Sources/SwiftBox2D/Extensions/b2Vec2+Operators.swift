import box2d

extension b2Vec2 {
    public static var zero: Self {
        b2Vec2_zero
    }
}

extension b2Vec2 {
    @inlinable
    public static func + (lhs: Self, rhs: Self) -> Self {
        binaryOp(lhs, rhs, +)
    }

    @inlinable
    public static func - (lhs: Self, rhs: Self) -> Self {
        binaryOp(lhs, rhs, -)
    }

    @inlinable
    public static func * (lhs: Self, rhs: Self) -> Self {
        binaryOp(lhs, rhs, *)
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
