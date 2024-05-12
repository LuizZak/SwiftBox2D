// HEADS UP!: Auto-generated file, changes made directly here will be overwritten by code generators.
// Generated by generate_types.py

import box2d

/// World identifier validation. Provides validation for up to 64K allocations.
internal extension B2World {
    /// World identifier validation. Provides validation for up to 64K allocations.
    func isValid() -> Bool {
        b2World_IsValid(id)
    }
    
    /// Simulate a world for one time step. This performs collision detection, integration, and constraint solution.
    /// @param worldId the world to simulate
    /// @param timeStep the amount of time to simulate, this should be a fixed number. Typically 1/60.
    /// @param subStepCount the number of sub-steps, increasing the sub-step count can increase accuracy. Typically 4.
    func step(_ timeStep: Float, _ subStepCount: Int32) {
        b2World_Step(id, timeStep, subStepCount)
    }
    
    /// Call this to draw shapes and other debug draw data. This is intentionally non-const.
    func draw(_ draw: UnsafeMutablePointer<b2DebugDraw>) {
        b2World_Draw(id, draw)
    }
    
    /// Get the body events for the current time step. The event data is transient. Do not store a reference to this data.
    func getBodyEvents() -> b2BodyEvents {
        b2World_GetBodyEvents(id)
    }
    
    /// Get sensor events for the current time step. The event data is transient. Do not store a reference to this data.
    func getSensorEvents() -> b2SensorEvents {
        b2World_GetSensorEvents(id)
    }
    
    /// Get contact events for this current time step. The event data is transient. Do not store a reference to this data.
    func getContactEvents() -> b2ContactEvents {
        b2World_GetContactEvents(id)
    }
    
    /// Overlap test for all shapes that *potentially* overlap the provided AABB.
    func overlapAABB(_ aabb: b2AABB, _ filter: b2QueryFilter, _ fcn: UnsafeMutablePointer<b2OverlapResultFcn>, _ context: UnsafeMutableRawPointer) {
        b2World_OverlapAABB(id, aabb, filter, fcn, context)
    }
    
    /// Overlap test for for all shapes that overlap the provided circle.
    func overlapCircle(_ circle: UnsafeMutablePointer<b2Circle>, _ transform: b2Transform, _ filter: b2QueryFilter, _ fcn: UnsafeMutablePointer<b2OverlapResultFcn>, _ context: UnsafeMutableRawPointer) {
        b2World_OverlapCircle(id, circle, transform, filter, fcn, context)
    }
    
    /// Overlap test for all shapes that overlap the provided capsule.
    func overlapCapsule(_ capsule: UnsafeMutablePointer<b2Capsule>, _ transform: b2Transform, _ filter: b2QueryFilter, _ fcn: UnsafeMutablePointer<b2OverlapResultFcn>, _ context: UnsafeMutableRawPointer) {
        b2World_OverlapCapsule(id, capsule, transform, filter, fcn, context)
    }
    
    /// Overlap test for all shapes that overlap the provided polygon.
    func overlapPolygon(_ polygon: UnsafeMutablePointer<b2Polygon>, _ transform: b2Transform, _ filter: b2QueryFilter, _ fcn: UnsafeMutablePointer<b2OverlapResultFcn>, _ context: UnsafeMutableRawPointer) {
        b2World_OverlapPolygon(id, polygon, transform, filter, fcn, context)
    }
    
    /// Ray-cast the world for all shapes in the path of the ray. Your callback
    /// controls whether you get the closest point, any point, or n-points.
    /// The ray-cast ignores shapes that contain the starting point.
    /// @param callback a user implemented callback class.
    /// @param point1 the ray starting point
    /// @param point2 the ray ending point
    func rayCast(_ origin: b2Vec2, _ translation: b2Vec2, _ filter: b2QueryFilter, _ fcn: UnsafeMutablePointer<b2CastResultFcn>, _ context: UnsafeMutableRawPointer) {
        b2World_RayCast(id, origin, translation, filter, fcn, context)
    }
    
    /// Ray-cast closest hit. Convenience function. This is less general than b2World_RayCast and does not allow for custom filtering.
    func rayCastClosest(_ origin: b2Vec2, _ translation: b2Vec2, _ filter: b2QueryFilter) -> b2RayResult {
        b2World_RayCastClosest(id, origin, translation, filter)
    }
    
    /// Cast a circle through the world. Similar to a ray-cast except that a circle is cast instead of a point.
    func circleCast(_ circle: UnsafeMutablePointer<b2Circle>, _ originTransform: b2Transform, _ translation: b2Vec2, _ filter: b2QueryFilter, _ fcn: UnsafeMutablePointer<b2CastResultFcn>, _ context: UnsafeMutableRawPointer) {
        b2World_CircleCast(id, circle, originTransform, translation, filter, fcn, context)
    }
    
    /// Cast a capsule through the world. Similar to a ray-cast except that a capsule is cast instead of a point.
    func capsuleCast(_ capsule: UnsafeMutablePointer<b2Capsule>, _ originTransform: b2Transform, _ translation: b2Vec2, _ filter: b2QueryFilter, _ fcn: UnsafeMutablePointer<b2CastResultFcn>, _ context: UnsafeMutableRawPointer) {
        b2World_CapsuleCast(id, capsule, originTransform, translation, filter, fcn, context)
    }
    
    /// Cast a capsule through the world. Similar to a ray-cast except that a polygon is cast instead of a point.
    func polygonCast(_ polygon: UnsafeMutablePointer<b2Polygon>, _ originTransform: b2Transform, _ translation: b2Vec2, _ filter: b2QueryFilter, _ fcn: UnsafeMutablePointer<b2CastResultFcn>, _ context: UnsafeMutableRawPointer) {
        b2World_PolygonCast(id, polygon, originTransform, translation, filter, fcn, context)
    }
    
    /// Enable/disable sleep. Advanced feature for testing.
    func enableSleeping(_ flag: Bool) {
        b2World_EnableSleeping(id, flag)
    }
    
    /// Enable/disable constraint warm starting. Advanced feature for testing.
    func enableWarmStarting(_ flag: Bool) {
        b2World_EnableWarmStarting(id, flag)
    }
    
    /// Enable/disable continuous collision. Advanced feature for testing.
    func enableContinuous(_ flag: Bool) {
        b2World_EnableContinuous(id, flag)
    }
    
    /// Adjust the restitution threshold. Advanced feature for testing.
    func setRestitutionThreshold(_ value: Float) {
        b2World_SetRestitutionThreshold(id, value)
    }
    
    /// Register the pre-solve callback. This is optional.
    func setPreSolveCallback(_ fcn: UnsafeMutablePointer<b2PreSolveFcn>, _ context: UnsafeMutableRawPointer) {
        b2World_SetPreSolveCallback(id, fcn, context)
    }
    
    /// Set the gravity vector for the entire world. Typically in m/s^2
    func setGravity(_ gravity: b2Vec2) {
        b2World_SetGravity(id, gravity)
    }
    
    /// @return the gravity vector
    func getGravity() -> b2Vec2 {
        b2World_GetGravity(id)
    }
    
    /// Apply explosion
    func explode(_ position: b2Vec2, _ radius: Float, _ impulse: Float) {
        b2World_Explode(id, position, radius, impulse)
    }
    
    /// Adjust contact tuning parameters:
    /// - hertz is the contact stiffness (cycles per second)
    /// - damping ratio is the contact bounciness with 1 being critical damping (non-dimensional)
    /// - push velocity is the maximum contact constraint push out velocity (meters per second)
    /// Advanced feature
    func setContactTuning(_ hertz: Float, _ dampingRatio: Float, _ pushVelocity: Float) {
        b2World_SetContactTuning(id, hertz, dampingRatio, pushVelocity)
    }
    
    /// Get the current profile
    func getProfile() -> b2Profile {
        b2World_GetProfile(id)
    }
    
    /// Get counters and sizes
    func getCounters() -> b2Counters {
        b2World_GetCounters(id)
    }
    
    /// Dump memory stats to box2d_memory.txt
    func dumpMemoryStats() {
        b2World_DumpMemoryStats(id)
    }
}