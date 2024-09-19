import box2d

public class B2Shape {
    var id: b2ShapeId

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
    public func destroy() {
        b2DestroyShape(id)

        id = b2_nullShapeId
    }
}
