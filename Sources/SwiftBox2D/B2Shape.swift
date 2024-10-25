import box2d

public class B2Shape {
    /// Gets the ID of this shape.
    private(set) public var id: b2ShapeId

    init(id: b2ShapeId) {
        self.id = id
    }

    /// Creates a new capsule shape, attaching it to a given body.
    public convenience init(body: B2Body, shape: b2ShapeDef, capsule: B2Capsule) {
        var shape = shape
        var capsule = capsule

        let id = b2CreateCapsuleShape(body.id, &shape, &capsule)

        self.init(id: id)
    }

    /// Creates a new circle shape, attaching it to a given body.
    public convenience init(body: B2Body, shape: b2ShapeDef, circle: B2Circle) {
        var shape = shape
        var circle = circle

        let id = b2CreateCircleShape(body.id, &shape, &circle)

        self.init(id: id)
    }

    /// Creates a new polygon shape, attaching it to a given body.
    public convenience init(body: B2Body, shape: b2ShapeDef, polygon: B2Polygon) {
        var shape = shape
        var polygon = polygon

        let id = b2CreatePolygonShape(body.id, &shape, &polygon)

        self.init(id: id)
    }

    /// Creates a new segment shape, attaching it to a given body.
    public convenience init(body: B2Body, shape: b2ShapeDef, segment: B2Segment) {
        var shape = shape
        var segment = segment

        let id = b2CreateSegmentShape(body.id, &shape, &segment)

        self.init(id: id)
    }

    /// Destroys this shape, removing it from the body that owns it.
    ///
    /// You may defer the body mass update which can improve performance if several shapes on a body are destroyed at once.
    /// - seealso: B2Body.applyMassFromShapes
    public func destroy(updateBodyMass: Bool) {
        b2DestroyShape(id, updateBodyMass)

        id = b2_nullShapeId
    }
}
