import box2d

extension B2Vec2 {
    /// Component-wise absolute vector
    @inlinable
    public var absolute: Self {
        return b2Abs(self)
    }
    
    /// Returns a copy of `self` converted into a unit vector if possible, otherwise returns the zero vector.
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
    
    /// Returns the angle, in radians, of this vector
    @inlinable
    public var angle: Float {
        return B2Rot(fromNormalized: normalized).angle
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
    
    @inlinable
    public func rotated(by rot: b2Rot) -> Self {
        return b2RotateVector(rot, self)
    }
    
    @inlinable
    public func inverseRotated(by rot: b2Rot) -> Self {
        return b2InvRotateVector(rot, self)
    }
    
    /// Component-wise clamp `self` into the range [a, b]
    @inlinable
    public func clamped(min a: Self, max b: Self) -> Self {
        return b2Clamp(self, a, b)
    }
    
    /// Converts `self` into a unit vector in-place if possible, otherwise converts `self` into the zero vector.
    @inlinable
    public mutating func normalize() {
        self = normalized
    }
}

extension B2Vec2 {
    /// Creates a unit vector from a given angle.
    @inlinable
    public static func fromAngle(_ angle: Float) -> B2Vec2 {
        let cosSin = b2ComputeCosSin(angle)
        return B2Vec2(x: cosSin.cosine, y: cosSin.sine)
    }
    
    /// Compute the rotation between two unit vectors.
    @inlinable
    public static func rotationBetween(unitA: Self, unitB: Self) -> B2Rot {
        return b2ComputeRotationBetweenUnitVectors(unitA, unitB)
    }
}
