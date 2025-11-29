import box2d

/// A prismatic (slider) joint.
///
/// This requires defining a line of motion using an axis and an anchor point.
/// The definition uses local anchor points and a local axis so that the initial
/// configuration can violate the constraint slightly. The joint translation is zero
/// when the local anchor points coincide in world space.
public class B2PrismaticJoint: B2Joint {
    /// Creates a prismatic joint from a given joint ID.
    ///
    /// - precondition: `id` represents a prismatic joint ID (`b2Joint_GetType(id) == b2JointType.b2PrismaticJoint`).
    public override init(id: b2JointId) {
        assert(b2Joint_GetType(id) == b2JointType.b2PrismaticJoint)

        super.init(id: id)
    }

    /// Creates a new prismatic joint.
    public init(world: B2World, _ def: b2PrismaticJointDef) {
        var def = def
        let id = b2CreatePrismaticJoint(world.id, &def)

        super.init(id: id)
    }
}
