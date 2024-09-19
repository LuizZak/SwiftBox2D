import box2d

public class B2World {
    /// Common callback function for ray and shape casts.
    public typealias CastResultCallback = (
        _ shapeId: b2ShapeId,
        _ point: b2Vec2,
        _ normal: b2Vec2,
        _ fraction: Float
    ) -> CastResult

    /// Common callback for overlap queries.
    public typealias OverlapResultCallback = (_ shapeId: b2ShapeId) -> Bool

    /// Gets the ID of this world.
    private(set) public var id: b2WorldId

    init(id: b2WorldId) {
        self.id = id
    }

    /// Initializes a new world with a given definition.
    public convenience init(_ def: b2WorldDef) {
        var def = def
        let id = b2CreateWorld(&def)

        self.init(id: id)
    }

    /// Initializes a new world.
    public convenience init() {
        var worldDef = b2DefaultWorldDef()
        worldDef.workerCount = 1
        worldDef.enqueueTask = _enqueueTask
        worldDef.finishTask = _finishTask
        worldDef.enableSleep = true

        self.init(worldDef)
    }

    deinit {
        b2DestroyWorld(id)
    }

    /// Simulate a world for one time step. This performs collision detection,
    /// integration, and constraint solution.
    ///
    /// - param timeStep: The amount of time to simulate, this should be a fixed
    ///     number. Typically 1/60.
    /// - param subStepCount: The number of sub-steps, increasing the sub-step
    ///     count can increase accuracy. Typically 4.
    public func step(_ timeStep: Float, subSteps: Int = 4) {
        step(timeStep, Int32(subSteps))
    }

    /// Overlap test for all shapes that *potentially* overlap the provided AABB.
    public func overlapAABB(
        _ aabb: B2AABB,
        filter: B2QueryFilter,
        callback: OverlapResultCallback
    ) {
        withoutActuallyEscaping(callback) { callback in
            withUnsafePointer(to: callback) { callback in
                overlapAABB(
                    aabb,
                    filter,
                    { (shapeId, ptr) in
                        let callback = ptr!.bindMemory(to: OverlapResultCallback.self, capacity: 1)

                        return callback.pointee(shapeId)
                    },
                    UnsafeMutableRawPointer(mutating: callback)
                )
            }
        }
    }

    /// Overlap test for for all shapes that overlap the provided circle.
    public func overlapCircle(
        _ circle: B2Circle,
        transform: B2Transform = .identity,
        filter: B2QueryFilter,
        callback: OverlapResultCallback
    ) {
        var circle = circle
        withoutActuallyEscaping(callback) { callback in
            withUnsafePointer(to: callback) { callback in
                overlapCircle(
                    &circle,
                    transform,
                    filter,
                    { (shapeId, ptr) in
                        let callback = ptr!.bindMemory(to: OverlapResultCallback.self, capacity: 1)

                        return callback.pointee(shapeId)
                    },
                    UnsafeMutableRawPointer(mutating: callback)
                )
            }
        }
    }

    /// Overlap test for for all shapes that overlap the provided capsule.
    public func overlapCapsule(
        _ capsule: B2Capsule,
        transform: B2Transform = .identity,
        filter: B2QueryFilter,
        callback: OverlapResultCallback
    ) {
        var capsule = capsule
        withoutActuallyEscaping(callback) { callback in
            withUnsafePointer(to: callback) { callback in
                overlapCapsule(
                    &capsule,
                    transform,
                    filter,
                    { (shapeId, ptr) in
                        let callback = ptr!.bindMemory(to: OverlapResultCallback.self, capacity: 1)

                        return callback.pointee(shapeId)
                    },
                    UnsafeMutableRawPointer(mutating: callback)
                )
            }
        }
    }

    /// Overlap test for for all shapes that overlap the provided polygon.
    public func overlapPolygon(
        _ polygon: B2Polygon,
        transform: B2Transform = .identity,
        filter: B2QueryFilter,
        callback: OverlapResultCallback
    ) {
        var polygon = polygon
        withoutActuallyEscaping(callback) { callback in
            withUnsafePointer(to: callback) { callback in
                overlapPolygon(
                    &polygon,
                    transform,
                    filter,
                    { (shapeId, ptr) in
                        let callback = ptr!.bindMemory(to: OverlapResultCallback.self, capacity: 1)

                        return callback.pointee(shapeId)
                    },
                    UnsafeMutableRawPointer(mutating: callback)
                )
            }
        }
    }

    /// Cast a ray into the world to collect shapes in the path of the ray.
    /// Your callback function controls whether you get the closest point, any
    /// point, or n-points.
    /// The ray-cast ignores shapes that contain the starting point.
    ///
    /// - parameter origin: The start point of the ray
    /// - parameter translation: The translation of the ray from the start point
    ///     to the end point
    /// - parameter filter: Contains bit flags to filter unwanted shapes from the results
    /// - parameter callback: A user implemented callback function
    ///
    /// - note: The callback function may receive shapes in any order
    public func castRay(
        origin: B2Vec2,
        translation: B2Vec2,
        filter: B2QueryFilter,
        callback: CastResultCallback
    ) {
        withoutActuallyEscaping(callback) { callback in
            withUnsafePointer(to: callback) { callback in
                castRay(
                    origin,
                    translation,
                    filter,
                    { (shapeId, point, normal, fraction, ptr) in
                        let callback = ptr!.bindMemory(to: CastResultCallback.self, capacity: 1)

                        switch callback.pointee(shapeId, point, normal, fraction) {
                        case .ignore:
                            return -1.0

                        case .terminate:
                            return 0.0

                        case .clip(let fraction):
                            return fraction

                        case .proceed:
                            return 1.0
                        }
                    },
                    UnsafeMutableRawPointer(mutating: callback)
                )
            }
        }
    }

    /// Cast a circle through the world. Similar to a cast ray except that a
    /// circle is cast instead of a point.
    ///
    /// Your callback function controls whether you get the closest point, any
    /// point, or n-points.
    /// The ray-cast ignores shapes that contain the starting point.
    ///
    /// - note: The callback function may receive shapes in any order
    public func castCircle(
        _ circle: B2Circle,
        originTransform: B2Transform = .identity,
        translation: B2Vec2,
        filter: B2QueryFilter,
        callback: CastResultCallback
    ) {
        var circle = circle
        withoutActuallyEscaping(callback) { callback in
            withUnsafePointer(to: callback) { callback in
                castCircle(
                    &circle,
                    originTransform,
                    translation,
                    filter,
                    { (shapeId, point, normal, fraction, ptr) in
                        let callback = ptr!.bindMemory(to: CastResultCallback.self, capacity: 1)

                        switch callback.pointee(shapeId, point, normal, fraction) {
                        case .ignore:
                            return -1.0

                        case .terminate:
                            return 0.0

                        case .clip(let fraction):
                            return fraction

                        case .proceed:
                            return 1.0
                        }
                    },
                    UnsafeMutableRawPointer(mutating: callback)
                )
            }
        }
    }

    /// Cast a capsule through the world. Similar to a cast ray except that a
    /// capsule is cast instead of a point.
    ///
    /// Your callback function controls whether you get the closest point, any
    /// point, or n-points.
    /// The ray-cast ignores shapes that contain the starting point.
    ///
    /// - note: The callback function may receive shapes in any order
    public func castCapsule(
        _ capsule: B2Capsule,
        originTransform: B2Transform = .identity,
        translation: B2Vec2,
        filter: B2QueryFilter,
        callback: CastResultCallback
    ) {
        var capsule = capsule
        withoutActuallyEscaping(callback) { callback in
            withUnsafePointer(to: callback) { callback in
                castCapsule(
                    &capsule,
                    originTransform,
                    translation,
                    filter,
                    { (shapeId, point, normal, fraction, ptr) in
                        let callback = ptr!.bindMemory(to: CastResultCallback.self, capacity: 1)

                        switch callback.pointee(shapeId, point, normal, fraction) {
                        case .ignore:
                            return -1.0

                        case .terminate:
                            return 0.0

                        case .clip(let fraction):
                            return fraction

                        case .proceed:
                            return 1.0
                        }
                    },
                    UnsafeMutableRawPointer(mutating: callback)
                )
            }
        }
    }

    /// Cast a polygon through the world. Similar to a cast ray except that a
    /// polygon is cast instead of a point.
    ///
    /// Your callback function controls whether you get the closest point, any
    /// point, or n-points.
    /// The ray-cast ignores shapes that contain the starting point.
    ///
    /// - note: The callback function may receive shapes in any order
    public func castPolygon(
        _ polygon: B2Polygon,
        originTransform: B2Transform = .identity,
        translation: B2Vec2,
        filter: B2QueryFilter,
        callback: CastResultCallback
    ) {
        var polygon = polygon
        withoutActuallyEscaping(callback) { callback in
            withUnsafePointer(to: callback) { callback in
                castPolygon(
                    &polygon,
                    originTransform,
                    translation,
                    filter,
                    { (shapeId, point, normal, fraction, ptr) in
                        let callback = ptr!.bindMemory(to: CastResultCallback.self, capacity: 1)

                        switch callback.pointee(shapeId, point, normal, fraction) {
                        case .ignore:
                            return -1.0

                        case .terminate:
                            return 0.0

                        case .clip(let fraction):
                            return fraction

                        case .proceed:
                            return 1.0
                        }
                    },
                    UnsafeMutableRawPointer(mutating: callback)
                )
            }
        }
    }

    // MARK: - Creation

    /// Creates a new body in this world.
    @discardableResult
    public func createBody(_ bodyDef: b2BodyDef) -> B2Body {
        return B2Body(world: self, bodyDef)
    }

    /// Creates a new distance joint in this world.
    @discardableResult
    public func createJoint(_ jointDef: b2DistanceJointDef) -> B2DistanceJoint {
        .init(world: self, jointDef)
    }

    /// Creates a new motor joint in this world.
    @discardableResult
    public func createJoint(_ jointDef: b2MotorJointDef) -> B2MotorJoint {
        .init(world: self, jointDef)
    }

    /// Creates a new mouse joint in this world.
    @discardableResult
    public func createJoint(_ jointDef: b2MouseJointDef) -> B2MouseJoint {
        .init(world: self, jointDef)
    }

    /// Creates a new prismatic joint in this world.
    @discardableResult
    public func createJoint(_ jointDef: b2PrismaticJointDef) -> B2PrismaticJoint {
        .init(world: self, jointDef)
    }

    /// Creates a new revolute joint in this world.
    @discardableResult
    public func createJoint(_ jointDef: b2RevoluteJointDef) -> B2RevoluteJoint {
        .init(world: self, jointDef)
    }

    /// Creates a new weld joint in this world.
    @discardableResult
    public func createJoint(_ jointDef: b2WeldJointDef) -> B2WeldJoint {
        .init(world: self, jointDef)
    }

    /// Creates a new wheel joint in this world.
    @discardableResult
    public func createJoint(_ jointDef: b2WheelJointDef) -> B2WheelJoint {
        .init(world: self, jointDef)
    }

    // MARK: - Auxiliary

    /// Expected result value returned by ray and shape cast result functions.
    public enum CastResult {
        /// Ignore the shape and continue.
        case ignore

        /// Terminate the ray cast.
        case terminate

        /// Clip the ray to a given fraction.
        case clip(fraction: Float)

        /// Don't clip the ray and proceed.
        case proceed
    }
}

private func _enqueueTask(_ task: (@convention(c) (Int32, Int32, UInt32, UnsafeMutableRawPointer?) -> Void)?, itemCount: Int32, minRange: Int32, taskContext: UnsafeMutableRawPointer?, userContext: UnsafeMutableRawPointer?) -> UnsafeMutableRawPointer? {
    task?(0, itemCount, 0, taskContext)

    return nil
}

private func _finishTask(_ task: UnsafeMutableRawPointer?, _ userContext: UnsafeMutableRawPointer?) {

}
