import box2d

public class B2Body {
    /// Gets the ID of this body.
    private(set) public var id: b2BodyId

    /// Instantiates a `B2Body` from a given body ID.
    public init(id: b2BodyId) {
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

    // MARK: - Creation

    /// Creates a new capsule shape on this body.
    @discardableResult
    public func createShape(_ capsule: B2Capsule, shapeDef: b2ShapeDef) -> B2Shape {
        B2Shape(body: self, shapeDef: shapeDef, capsule: capsule)
    }

    /// Creates a new circle shape on this body.
    @discardableResult
    public func createShape(_ circle: B2Circle, shapeDef: b2ShapeDef) -> B2Shape {
        B2Shape(body: self, shapeDef: shapeDef, circle: circle)
    }

    /// Creates a new polygon shape on this body.
    @discardableResult
    public func createShape(_ polygon: B2Polygon, shapeDef: b2ShapeDef) -> B2Shape {
        B2Shape(body: self, shapeDef: shapeDef, polygon: polygon)
    }

    /// Creates a new segment shape on this body.
    @discardableResult
    public func createShape(_ segment: B2Segment, shapeDef: b2ShapeDef) -> B2Shape {
        B2Shape(body: self, shapeDef: shapeDef, segment: segment)
    }
}
