import box2d

/// A prismatic (slider) joint.
///
/// This requires defining a line of motion using an axis and an anchor point.
/// The definition uses local anchor points and a local axis so that the initial
/// configuration can violate the constraint slightly. The joint translation is zero
/// when the local anchor points coincide in world space.
public class B2PrismaticJoint: B2Joint {
    /// Creates a new prismatic joint.
    public init(world: B2World, _ def: b2PrismaticJointDef) {
        var def = def
        let id = b2CreatePrismaticJoint(world.id, &def)

        super.init(id: id)
    }
}
