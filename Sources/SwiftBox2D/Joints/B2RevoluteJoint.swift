import box2d

/// A revolute (hinge) joint.
public class B2RevoluteJoint: B2Joint {
    /// Creates a new revolute joint.
    public init(world: B2World, _ def: b2RevoluteJointDef) {
        var def = def
        let id = b2CreateRevoluteJoint(world.id, &def)

        super.init(id: id)
    }
}
