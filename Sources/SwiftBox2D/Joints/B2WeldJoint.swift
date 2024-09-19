import box2d

/// A weld joint.
public class B2WeldJoint: B2Joint {
    /// Creates a new weld joint.
    public init(world: B2World, _ def: b2WeldJointDef) {
        var def = def
        let id = b2CreateWeldJoint(world.id, &def)

        super.init(id: id)
    }
}
