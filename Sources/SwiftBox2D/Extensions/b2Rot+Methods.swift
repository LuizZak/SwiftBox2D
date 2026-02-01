import box2d

extension B2Rot {
    @inlinable
    public var inverse: Self {
        return b2InvertRot(self)
    }
    
    @inlinable
    public var normalized: Self {
        return b2NormalizeRot(self)
    }
    
    @inlinable
    public var isNormalized: Bool {
        return b2IsNormalizedRot(self)
    }
}
