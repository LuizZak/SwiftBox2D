import box2d

/// A mouse joint.
///
/// This a soft constraint and allows the constraint to stretch without
/// applying huge forces. This also applies rotation constraint heuristic to improve control.
public class B2MouseJoint: B2Joint {
    /// Creates a new mouse joint.
    public init(world: B2World, _ def: b2MouseJointDef) {
        var def = def
        let id = b2CreateMouseJoint(world.id, &def)

        super.init(id: id)
    }
}
