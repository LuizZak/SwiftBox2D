import box2d

/// A revolute (hinge) joint.
///
/// This requires defining an anchor point where the bodies are joined.
/// The definition uses local anchor points so that the
/// initial configuration can violate the constraint slightly. You also need to
/// specify the initial relative angle for joint limits. This helps when saving
/// and loading a game.
/// The local anchor points are measured from the body's origin
/// rather than the center of mass because:
/// 1. you might not know where the center of mass will be
/// 2. if you add/remove shapes from a body and recompute the mass, the joints will be broken
public class B2RevoluteJoint: B2Joint {
    /// Creates a new revolute joint.
    public init(world: B2World, _ def: b2RevoluteJointDef) {
        var def = def
        let id = b2CreateRevoluteJoint(world.id, &def)

        super.init(id: id)
    }
}
