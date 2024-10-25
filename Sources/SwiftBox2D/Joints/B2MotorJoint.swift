import box2d

/// A motor joint is used to control the relative motion between two bodies
///
/// A typical usage is to control the movement of a dynamic body with respect to
/// the ground.
public class B2MotorJoint: B2Joint {
    /// Creates a new motor joint.
    public init(world: B2World, _ def: b2MotorJointDef) {
        var def = def
        let id = b2CreateMotorJoint(world.id, &def)

        super.init(id: id)
    }
}
