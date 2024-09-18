import box2d

public class B2Body {
    var id: b2BodyId

    init(id: b2BodyId) {
        self.id = id
    }

    /// Creates a new rigid body with a given definition on a given world.
    public convenience init(world: B2World, _ def: b2BodyDef) {
        var def = def
        let id = b2CreateBody(world.id, &def)

        self.init(id: id)
    }

    /// Destroys this body reference, removing it from the world.
    public func destroy() {
        b2DestroyBody(self.id)

        self.id = b2_nullBodyId
    }
}
