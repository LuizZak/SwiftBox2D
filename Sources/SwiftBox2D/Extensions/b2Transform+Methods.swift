import box2d

extension b2Transform {
    /// Transform a point (e.g. local space to world space)
    public func transform(_ point: B2Vec2) -> B2Vec2 {
        b2TransformPoint(self, point)
    }
    
    /// Inverse transform a point (e.g. world space to local space)
    public func inverseTransform(_ point: B2Vec2) -> B2Vec2 {
        b2InvTransformPoint(self, point)
    }
    
    /// Transforms `rhs` by `lhs`.
    /// Equivalent to `lhs.transform(rhs)`
    public static func * (lhs: Self, rhs: B2Vec2) -> B2Vec2 {
        return lhs.transform(rhs)
    }
    
    /// Transforms `lhs` by `rhs`.
    /// Equivalent to `rhs.transform(lhs)`
    public static func * (lhs: B2Vec2, rhs: Self) -> B2Vec2 {
        return rhs.transform(lhs)
    }
    
    /// Transforms `lhs` by `rhs`.
    /// Equivalent to `lhs = rhs.transform(lhs)`
    public static func *= (lhs: inout B2Vec2, rhs: Self) {
        lhs = lhs * rhs
    }
    
    /// Multiplies two transforms together.
    public static func * (lhs: Self, rhs: Self) -> Self {
        return b2MulTransforms(lhs, rhs)
    }
}
