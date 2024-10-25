// HEADS UP!: Auto-generated file, changes made directly here will be overwritten by code generators.
// Generated by generate_types.py

import box2d

public extension B2Shape {
    /// Shape identifier validation. Provides validation for up to 64K allocations.
    func isValid() -> Bool {
        b2Shape_IsValid(id)
    }
    
    /// Get the type of a shape
    func getType() -> B2ShapeType {
        b2Shape_GetType(id)
    }
    
    /// Get the id of the body that a shape is attached to
    func getBody() -> b2BodyId {
        b2Shape_GetBody(id)
    }
    
    /// Get the world that owns this shape
    func getWorld() -> b2WorldId {
        b2Shape_GetWorld(id)
    }
    
    /// Returns true If the shape is a sensor
    func isSensor() -> Bool {
        b2Shape_IsSensor(id)
    }
    
    /// Set the user data for a shape
    func setUserData(_ userData: UnsafeMutableRawPointer?) {
        b2Shape_SetUserData(id, userData)
    }
    
    /// Set the mass density of a shape, typically in kg/m^2.
    /// This will optionally update the mass properties on the parent body.
    /// @see b2ShapeDef::density, b2Body_ApplyMassFromShapes
    func setDensity(_ density: Float, _ updateBodyMass: Bool) {
        b2Shape_SetDensity(id, density, updateBodyMass)
    }
    
    /// Get the density of a shape, typically in kg/m^2
    func getDensity() -> Float {
        b2Shape_GetDensity(id)
    }
    
    /// Enable sensor events for this shape. Only applies to kinematic and dynamic bodies. Ignored for sensors.
    /// @see b2ShapeDef::isSensor
    func enableSensorEvents(_ flag: Bool) {
        b2Shape_EnableSensorEvents(id, flag)
    }
    
    /// Returns true if sensor events are enabled
    func areSensorEventsEnabled() -> Bool {
        b2Shape_AreSensorEventsEnabled(id)
    }
    
    /// Enable contact events for this shape. Only applies to kinematic and dynamic bodies. Ignored for sensors.
    /// @see b2ShapeDef::enableContactEvents
    func enableContactEvents(_ flag: Bool) {
        b2Shape_EnableContactEvents(id, flag)
    }
    
    /// Returns true if contact events are enabled
    func areContactEventsEnabled() -> Bool {
        b2Shape_AreContactEventsEnabled(id)
    }
    
    /// Enable pre-solve contact events for this shape. Only applies to dynamic bodies. These are expensive
    /// and must be carefully handled due to multithreading. Ignored for sensors.
    /// @see b2PreSolveFcn
    func enablePreSolveEvents(_ flag: Bool) {
        b2Shape_EnablePreSolveEvents(id, flag)
    }
    
    /// Returns true if pre-solve events are enabled
    func arePreSolveEventsEnabled() -> Bool {
        b2Shape_ArePreSolveEventsEnabled(id)
    }
    
    /// Enable contact hit events for this shape. Ignored for sensors.
    /// @see b2WorldDef.hitEventThreshold
    func enableHitEvents(_ flag: Bool) {
        b2Shape_EnableHitEvents(id, flag)
    }
    
    /// Returns true if hit events are enabled
    func areHitEventsEnabled() -> Bool {
        b2Shape_AreHitEventsEnabled(id)
    }
    
    /// Test a point for overlap with a shape
    func testPoint(_ point: B2Vec2) -> Bool {
        b2Shape_TestPoint(id, point)
    }
    
    /// Ray cast a shape directly
    func rayCast(_ input: UnsafeMutablePointer<b2RayCastInput>?) -> b2CastOutput {
        b2Shape_RayCast(id, input)
    }
    
    /// Get a copy of the shape's circle. Asserts the type is correct.
    func getCircle() -> B2Circle {
        b2Shape_GetCircle(id)
    }
    
    /// Get a copy of the shape's line segment. Asserts the type is correct.
    func getSegment() -> B2Segment {
        b2Shape_GetSegment(id)
    }
    
    /// Get a copy of the shape's chain segment. These come from chain shapes.
    /// Asserts the type is correct.
    func getChainSegment() -> b2ChainSegment {
        b2Shape_GetChainSegment(id)
    }
    
    /// Get a copy of the shape's capsule. Asserts the type is correct.
    func getCapsule() -> B2Capsule {
        b2Shape_GetCapsule(id)
    }
    
    /// Get a copy of the shape's convex polygon. Asserts the type is correct.
    func getPolygon() -> B2Polygon {
        b2Shape_GetPolygon(id)
    }
    
    /// Allows you to change a shape to be a circle or update the current circle.
    /// This does not modify the mass properties.
    /// @see b2Body_ApplyMassFromShapes
    func setCircle(_ circle: UnsafeMutablePointer<b2Circle>?) {
        b2Shape_SetCircle(id, circle)
    }
    
    /// Allows you to change a shape to be a capsule or update the current capsule.
    /// This does not modify the mass properties.
    /// @see b2Body_ApplyMassFromShapes
    func setCapsule(_ capsule: UnsafeMutablePointer<b2Capsule>?) {
        b2Shape_SetCapsule(id, capsule)
    }
    
    /// Allows you to change a shape to be a segment or update the current segment.
    func setSegment(_ segment: UnsafeMutablePointer<b2Segment>?) {
        b2Shape_SetSegment(id, segment)
    }
    
    /// Allows you to change a shape to be a polygon or update the current polygon.
    /// This does not modify the mass properties.
    /// @see b2Body_ApplyMassFromShapes
    func setPolygon(_ polygon: UnsafeMutablePointer<b2Polygon>?) {
        b2Shape_SetPolygon(id, polygon)
    }
    
    /// Get the parent chain id if the shape type is a chain segment, otherwise
    /// returns b2_nullChainId.
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
    func getAABB() -> B2AABB {
        b2Shape_GetAABB(id)
    }
    
    /// Get the closest point on a shape to a target point. Target and result are in world space.
    func getClosestPoint(_ target: B2Vec2) -> B2Vec2 {
        b2Shape_GetClosestPoint(id, target)
    }
    
    ///  Get the friction of a shape
    /// Set the friction on a shape
    /// @see b2ShapeDef::friction
    var friction: Float {
        get {
            b2Shape_GetFriction(id)
        }
        set(friction) {
            b2Shape_SetFriction(id, friction)
        }
    }
    
    ///  Get the shape restitution
    /// Set the shape restitution (bounciness)
    /// @see b2ShapeDef::restitution
    var restitution: Float {
        get {
            b2Shape_GetRestitution(id)
        }
        set(restitution) {
            b2Shape_SetRestitution(id, restitution)
        }
    }
    
    ///  Get the shape filter
    /// Set the current filter. This is almost as expensive as recreating the shape.
    /// @see b2ShapeDef::filter
    var filter: b2Filter {
        get {
            b2Shape_GetFilter(id)
        }
        set(filter) {
            b2Shape_SetFilter(id, filter)
        }
    }
}
