import box2d

/// A distance joint.
///
/// This requires defining an anchor point on both bodies and the non-zero distance
/// of the distance joint. The definition uses local anchor points so that the
/// initial configuration can violate the constraint slightly. This helps when
/// saving and loading a game.
public class B2DistanceJoint: B2Joint {
    /// Creates a distance joint from a given joint ID.
    ///
    /// - precondition: `id` represents a distance joint ID (`b2Joint_GetType(id) == b2JointType.b2DistanceJoint`).
    public override init(id: b2JointId) {
        assert(b2Joint_GetType(id) == b2JointType.b2DistanceJoint)

        super.init(id: id)
    }

    /// Creates a new distance joint.
    public init(world: B2World, _ def: b2DistanceJointDef) {
        var def = def
        let id = b2CreateDistanceJoint(world.id, &def)

        super.init(id: id)
    }
}
