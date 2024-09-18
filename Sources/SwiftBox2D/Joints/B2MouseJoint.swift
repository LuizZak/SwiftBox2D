import box2d

/// A mouse joint.
public class B2MouseJoint: B2Joint {
    /// Creates a new mouse joint.
    public init(world: B2World, _ def: b2MouseJointDef) {
        var def = def
        let id = b2CreateMouseJoint(world.id, &def)

        super.init(id: id)
    }
}
