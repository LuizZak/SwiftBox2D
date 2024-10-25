import box2d

/// A weld joint.
///
/// A weld joint connect to bodies together rigidly. This constraint provides springs to mimic
/// soft-body simulation.
/// -note: The approximate solver in Box2D cannot hold many bodies together rigidly
public class B2WeldJoint: B2Joint {
    /// Creates a new weld joint.
    public init(world: B2World, _ def: b2WeldJointDef) {
        var def = def
        let id = b2CreateWeldJoint(world.id, &def)

        super.init(id: id)
    }
}
