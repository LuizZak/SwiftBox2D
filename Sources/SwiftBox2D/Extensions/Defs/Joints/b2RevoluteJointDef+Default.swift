import box2d

extension b2RevoluteJointDef {
    /// Use this to initialize your revolute joint definition.
    public static func `default`() -> Self {
        return b2DefaultRevoluteJointDef()
    }
}

extension b2RevoluteJointDef {
    /// Gets or sets the first attached body on this joint.
    ///
    /// Note: Instances returned will always be different identity-wise (`===`) to ones previously set.
    public var bodyA: B2Body {
        get { return B2Body(id: base.bodyIdA) }
        set { base.bodyIdA = newValue.id }
    }
    
    /// Gets or sets the second attached body on this joint.
    ///
    /// Note: Instances returned will always be different identity-wise (`===`) to ones previously set.
    public var bodyB: B2Body {
        get { return B2Body(id: base.bodyIdB) }
        set { base.bodyIdB = newValue.id }
    }
}
