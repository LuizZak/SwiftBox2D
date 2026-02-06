import box2d

extension b2JointDef {
    /// Gets or sets the first attached body on this joint.
    ///
    /// Note: Instances returned will always be different identity-wise (`===`) to ones previously set.
    public var bodyA: B2Body {
        get { return B2Body(id: bodyIdA) }
        set { bodyIdA = newValue.id }
    }
    
    /// Gets or sets the second attached body on this joint.
    ///
    /// Note: Instances returned will always be different identity-wise (`===`) to ones previously set.
    public var bodyB: B2Body {
        get { return B2Body(id: bodyIdB) }
        set { bodyIdB = newValue.id }
    }
}
