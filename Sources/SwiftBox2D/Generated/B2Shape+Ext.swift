// HEADS UP!: Auto-generated file, changes made directly here will be overwritten by code generators.
// Generated by generate_types.py

import box2d

/// Shape identifier validation. Provides validation for up to 64K allocations.
public extension B2Shape {
    /// Shape identifier validation. Provides validation for up to 64K allocations.
    func isValid() -> Bool {
        b2Shape_IsValid(id)
    }
    
    /// Get the type of a shape.
    func getType() -> b2ShapeType {
        b2Shape_GetType(id)
    }
    
    /// Get the body that a shape is attached to
    func getBody() -> b2BodyId {
        b2Shape_GetBody(id)
    }
    
    /// Is this shape a sensor? See b2ShapeDef.
    func isSensor() -> Bool {
        b2Shape_IsSensor(id)
    }
    
    /// Set the user data for a shape.
    func setUserData(_ userData: UnsafeMutableRawPointer?) {
        b2Shape_SetUserData(id, userData)
    }
    
    /// Set the density on a shape. Normally this is specified in b2ShapeDef.
    /// This will not update the mass properties on the parent body until you
    /// call b2Body_ResetMassData.
    func setDensity(_ density: Float) {
        b2Shape_SetDensity(id, density)
    }
    
    /// Get the density on a shape.
    func getDensity() -> Float {
        b2Shape_GetDensity(id)
    }
    
    /// Set the friction on a shape. Normally this is specified in b2ShapeDef.
    func setFriction(_ friction: Float) {
        b2Shape_SetFriction(id, friction)
    }
    
    /// Get the friction on a shape.
    func getFriction() -> Float {
        b2Shape_GetFriction(id)
    }
    
    /// Set the restitution (bounciness) on a shape. Normally this is specified in b2ShapeDef.
    func setRestitution(_ restitution: Float) {
        b2Shape_SetRestitution(id, restitution)
    }
    
    /// Get the restitution on a shape.
    func getRestitution() -> Float {
        b2Shape_GetRestitution(id)
    }
    
    /// Get the current filter
    func getFilter() -> b2Filter {
        b2Shape_GetFilter(id)
    }
    
    /// Set the current filter. This is almost as expensive as recreating the shape.
    func setFilter(_ filter: b2Filter) {
        b2Shape_SetFilter(id, filter)
    }
    
    /// Enable sensor events for this shape. Only applies to kinematic and dynamic bodies. Ignored for sensors.
    func enableSensorEvents(_ flag: Bool) {
        b2Shape_EnableSensorEvents(id, flag)
    }
    
    /// - returns: are sensor events enabled?
    func areSensorEventsEnabled() -> Bool {
        b2Shape_AreSensorEventsEnabled(id)
    }
    
    /// Enable contact events for this shape. Only applies to kinematic and dynamic bodies. Ignored for sensors.
    func enableContactEvents(_ flag: Bool) {
        b2Shape_EnableContactEvents(id, flag)
    }
    
    /// - returns: are contact events enabled?
    func areContactEventsEnabled() -> Bool {
        b2Shape_AreContactEventsEnabled(id)
    }
    
    /// Enable pre-solve contact events for this shape. Only applies to dynamic bodies. These are expensive
    /// and must be carefully handled due to multi-threading. Ignored for sensors.
    func enablePreSolveEvents(_ flag: Bool) {
        b2Shape_EnablePreSolveEvents(id, flag)
    }
    
    /// - returns: are pre-solve events enabled?
    func arePreSolveEventsEnabled() -> Bool {
        b2Shape_ArePreSolveEventsEnabled(id)
    }
    
    /// Enable contact hit events for this shape. Ignored for sensors.
    /// @see b2WorldDef.hitEventThreshold
    func enableHitEvents(_ flag: Bool) {
        b2Shape_EnableHitEvents(id, flag)
    }
    
    /// - returns: are hit events enabled?
    func areHitEventsEnabled() -> Bool {
        b2Shape_AreHitEventsEnabled(id)
    }
    
    /// Test a point for overlap with a shape
    func testPoint(_ point: b2Vec2) -> Bool {
        b2Shape_TestPoint(id, point)
    }
    
    /// Ray cast a shape directly
    func rayCast(_ origin: b2Vec2, _ translation: b2Vec2) -> b2CastOutput {
        b2Shape_RayCast(id, origin, translation)
    }
    
    /// Access the circle geometry of a shape. Asserts the type is correct.
    func getCircle() -> b2Circle {
        b2Shape_GetCircle(id)
    }
    
    /// Access the line segment geometry of a shape. Asserts the type is correct.
    func getSegment() -> b2Segment {
        b2Shape_GetSegment(id)
    }
    
    /// Access the smooth line segment geometry of a shape. These come from chain shapes.
    /// Asserts the type is correct.
    func getSmoothSegment() -> b2SmoothSegment {
        b2Shape_GetSmoothSegment(id)
    }
    
    /// Access the capsule geometry of a shape. Asserts the type is correct.
    func getCapsule() -> b2Capsule {
        b2Shape_GetCapsule(id)
    }
    
    /// Access the convex polygon geometry of a shape. Asserts the type is correct.
    func getPolygon() -> b2Polygon {
        b2Shape_GetPolygon(id)
    }
    
    /// Allows you to change a shape to be a circle or update the current circle.
    /// This does not modify the mass properties.
    func setCircle(_ circle: UnsafeMutablePointer<b2Circle>?) {
        b2Shape_SetCircle(id, circle)
    }
    
    /// Allows you to change a shape to be a capsule or update the current capsule.
    /// This does not modify the mass properties.
    func setCapsule(_ capsule: UnsafeMutablePointer<b2Capsule>?) {
        b2Shape_SetCapsule(id, capsule)
    }
    
    /// Allows you to change a shape to be a segment or update the current segment.
    /// This does not modify the mass properties.
    func setSegment(_ segment: UnsafeMutablePointer<b2Segment>?) {
        b2Shape_SetSegment(id, segment)
    }
    
    /// Allows you to change a shape to be a segment or update the current segment.
    /// This does not modify the mass properties.
    func setPolygon(_ polygon: UnsafeMutablePointer<b2Polygon>?) {
        b2Shape_SetPolygon(id, polygon)
    }
    
    /// If the type is b2_smoothSegmentShape then you can get the parent chain id.
    /// If the shape is not a smooth segment then this will return b2_nullChainId.
    func getParentChain() -> b2ChainId {
        b2Shape_GetParentChain(id)
    }
    
    /// Get the maximum capacity required for retrieving all the touching contacts on a shape
    func getContactCapacity() -> Int32 {
        b2Shape_GetContactCapacity(id)
    }
    
    /// Get the touching contact data for a shape. The provided shapeId will be either shapeIdA or shapeIdB on the contact data.
    func getContactData(_ contactData: UnsafeMutablePointer<b2ContactData>?, _ capacity: Int32) -> Int32 {
        b2Shape_GetContactData(id, contactData, capacity)
    }
    
    /// Get the current world AABB
    func getAABB() -> b2AABB {
        b2Shape_GetAABB(id)
    }
    
    /// Get the closest point on a shape to a target point. Target and result are in world space.
    func getClosestPoint(_ target: b2Vec2) -> b2Vec2 {
        b2Shape_GetClosestPoint(id, target)
    }
}
