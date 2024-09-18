import box2d

/// A weld joint.
public class B2WeldJoint: B2Joint {
    /// Creates a new weld joint.
    public init(world: B2World, _ def: b2RevoluteJointDef) {
        var def = def
        let id = b2CreateRevoluteJoint(world.id, &def)

        super.init(id: id)
    }
}
