import box2d

/// A prismatic (slider) joint.
public class B2PrismaticJoint: B2Joint {
    /// Creates a new prismatic joint.
    public init(world: B2World, _ def: b2PrismaticJointDef) {
        var def = def
        let id = b2CreatePrismaticJoint(world.id, &def)

        super.init(id: id)
    }
}
