import box2d

extension B2Vec2 {
    @inlinable
    public var absolute: Self {
        return b2Abs(self)
    }
    
    @inlinable
    public var normalized: Self {
        return b2Normalize(self)
    }
    
    @inlinable
    public var isNormalized: Bool {
        return b2IsNormalized(self)
    }
    
    @inlinable
    public var length: Float {
        return b2Length(self)
    }
    
    @inlinable
    public var lengthSquared: Float {
        return b2LengthSquared(self)
    }
    
    @inlinable
    public func dot(_ other: Self) -> Float {
        return b2Dot(self, other)
    }
    
    @inlinable
    public func cross(_ other: Self) -> Float {
        return b2Cross(self, other)
    }
    
    @inlinable
    public func leftPerpendicular() -> Self {
        return b2LeftPerp(self)
    }
    
    @inlinable
    public func rightPerpendicular() -> Self {
        return b2RightPerp(self)
    }
    
    @inlinable
    public func lerp(_ other: Self, _ t: Float) -> Self {
        return b2Lerp(self, other, t)
    }
    
    @inlinable
    public func distance(to other: Self) -> Float {
        return b2Distance(self, other)
    }
    
    @inlinable
    public func distanceSquared(to other: Self) -> Float {
        return b2DistanceSquared(self, other)
    }
}
