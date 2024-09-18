import box2d

public class B2Shape {
    var id: b2ShapeId

    init(id: b2ShapeId) {
        self.id = id
    }

    /// Creates a new capsule shape, attaching it to a given body.
    public convenience init(body: B2Body, shape: b2ShapeDef, capsule: b2Capsule) {
        var shape = shape
        var capsule = capsule

        let id = b2CreateCapsuleShape(body.id, &shape, &capsule)

        self.init(id: id)
    }

    /// Creates a new circle shape, attaching it to a given body.
    public convenience init(body: B2Body, shape: b2ShapeDef, circle: b2Circle) {
        var shape = shape
        var circle = circle

        let id = b2CreateCircleShape(body.id, &shape, &circle)

        self.init(id: id)
    }

    /// Creates a new polygon shape, attaching it to a given body.
    public convenience init(body: B2Body, shape: b2ShapeDef, polygon: b2Polygon) {
        var shape = shape
        var polygon = polygon

        let id = b2CreatePolygonShape(body.id, &shape, &polygon)

        self.init(id: id)
    }

    /// Creates a new segment shape, attaching it to a given body.
    public convenience init(body: B2Body, shape: b2ShapeDef, segment: b2Segment) {
        var shape = shape
        var segment = segment

        let id = b2CreateSegmentShape(body.id, &shape, &segment)

        self.init(id: id)
    }
}
