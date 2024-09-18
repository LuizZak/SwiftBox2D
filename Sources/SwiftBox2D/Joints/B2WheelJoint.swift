import box2d

/// A wheel joint.
public class B2WheelJoint: B2Joint {
    /// Creates a new wheel joint.
    public init(world: B2World, _ def: b2WheelJointDef) {
        var def = def
        let id = b2CreateWheelJoint(world.id, &def)

        super.init(id: id)
    }
}
