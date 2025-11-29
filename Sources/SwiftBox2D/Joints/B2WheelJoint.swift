import box2d

/// A wheel joint.
///
/// This requires defining a line of motion using an axis and an anchor point.
/// The definition uses local  anchor points and a local axis so that the initial
/// configuration can violate the constraint slightly. The joint translation is zero
/// when the local anchor points coincide in world space.
public class B2WheelJoint: B2Joint {
    /// Creates a wheel joint from a given joint ID.
    ///
    /// - precondition: `id` represents a wheel joint ID (`b2Joint_GetType(id) == b2JointType.b2WheelJoint`).
    public override init(id: b2JointId) {
        assert(b2Joint_GetType(id) == b2JointType.b2WheelJoint)

        super.init(id: id)
    }

    /// Creates a new wheel joint.
    public init(world: B2World, _ def: b2WheelJointDef) {
        var def = def
        let id = b2CreateWheelJoint(world.id, &def)

        super.init(id: id)
    }
}
