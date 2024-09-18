import box2d

/// A distance joint.
public class B2DistanceJoint: B2Joint {
    /// Creates a new distance joint.
    public init(world: B2World, _ def: b2DistanceJointDef) {
        var def = def
        let id = b2CreateDistanceJoint(world.id, &def)

        super.init(id: id)
    }
}
