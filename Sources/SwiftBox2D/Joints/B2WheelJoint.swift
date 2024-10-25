import box2d

/// A wheel joint.
///
/// This requires defining a line of motion using an axis and an anchor point.
/// The definition uses local  anchor points and a local axis so that the initial
/// configuration can violate the constraint slightly. The joint translation is zero
/// when the local anchor points coincide in world space.
public class B2WheelJoint: B2Joint {
    /// Creates a new wheel joint.
    public init(world: B2World, _ def: b2WheelJointDef) {
        var def = def
        let id = b2CreateWheelJoint(world.id, &def)

        super.init(id: id)
    }
}
