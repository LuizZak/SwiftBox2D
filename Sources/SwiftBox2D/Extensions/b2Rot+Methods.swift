import box2d

extension B2Rot {
    @inlinable
    public var xAxis: B2Vec2 {
        return b2Rot_GetXAxis(self)
    }
    
    @inlinable
    public var yAxis: B2Vec2 {
        return b2Rot_GetYAxis(self)
    }
    
    /// Get the angle in radians in the range [-pi, pi]
    @inlinable
    public var angle: Float {
        return b2Rot_GetAngle(self)
    }
    
    /// Get the inverse of this rotation
    @inlinable
    public var inverse: Self {
        return b2InvertRot(self)
    }
    
    /// Normalize rotation
    @inlinable
    public var normalized: Self {
        return b2NormalizeRot(self)
    }
    
    /// Is this rotation normalized?
    @inlinable
    public var isNormalized: Bool {
        return b2IsNormalizedRot(self)
    }
    
    /// Relative angle between `self` and `other`
    @inlinable
    public func relative(to other: Self) -> Float {
        return b2RelativeAngle(self, other)
    }
    
    /// Normalized linear interpolation
    /// https://fgiesen.wordpress.com/2012/08/15/linear-interpolation-past-present-and-future/
    ///    https://web.archive.org/web/20170825184056/http://number-none.com/product/Understanding%20Slerp,%20Then%20Not%20Using%20It/
    @inlinable
    public func normalizedLerp(to other: Self, factor: Float) -> Self {
        return b2NLerp(self, other, factor)
    }
    
    /// Compute the angular velocity necessary to rotate between `self` towards `other` rotations
    /// over a given (inverse) time.
    @inlinable
    public func computeAngularVelocity(to other: Self, inverseTimeStep: Float) -> Float {
        return b2ComputeAngularVelocity(self, other, inverseTimeStep)
    }
}

extension B2Rot {
    /// Make a rotation using an angle in radians
    @inlinable
    public init(fromRadians radians: Float) {
        self = b2MakeRot(radians)
    }
    
    /// Make a rotation using a unit vector
    ///
    /// - precondition: `vector` is a normalized vector (`vector.isNormalized == true`).
    @inlinable
    public init(fromNormalized vector: B2Vec2) {
        self = b2MakeRotFromUnitVector(vector)
    }
}
