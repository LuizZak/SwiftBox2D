import box2d

/// A null joint.
///
/// A null joint is used to disable collision between two specific bodies.
public class B2NullJoint: B2Joint {
    /// Creates a new null joint.
    public init(world: B2World, _ def: b2NullJointDef) {
        var def = def
        let id = b2CreateNullJoint(world.id, &def)

        super.init(id: id)
    }
}
