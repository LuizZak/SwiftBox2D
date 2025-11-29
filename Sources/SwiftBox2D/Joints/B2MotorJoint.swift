import box2d

/// A motor joint is used to control the relative motion between two bodies
///
/// A typical usage is to control the movement of a dynamic body with respect to
/// the ground.
public class B2MotorJoint: B2Joint {
    /// Creates a motor joint from a given joint ID.
    ///
    /// - precondition: `id` represents a motor joint ID (`b2Joint_GetType(id) == b2JointType.b2MotorJoint`).
    public override init(id: b2JointId) {
        assert(b2Joint_GetType(id) == b2JointType.b2MotorJoint)

        super.init(id: id)
    }

    /// Creates a new motor joint.
    public init(world: B2World, _ def: b2MotorJointDef) {
        var def = def
        let id = b2CreateMotorJoint(world.id, &def)

        super.init(id: id)
    }
}
