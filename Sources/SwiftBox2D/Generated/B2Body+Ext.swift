// HEADS UP!: Auto-generated file, changes made directly here will be overwritten by code generators.
// Generated by generate_types.py

import box2d

public extension B2Body {
    /// Body identifier validation. Can be used to detect orphaned ids. Provides validation for up to 64K allocations.
    func isValid() -> Bool {
        b2Body_IsValid(id)
    }
    
    /// Set the body name. Up to 31 characters excluding 0 termination.
    func setName(_ name: UnsafeMutablePointer<CChar>?) {
        b2Body_SetName(id, name)
    }
    
    /// Set the user data for a body
    func setUserData(_ userData: UnsafeMutableRawPointer?) {
        b2Body_SetUserData(id, userData)
    }
    
    /// Get the world position of a body. This is the location of the body origin.
    func getPosition() -> B2Vec2 {
        b2Body_GetPosition(id)
    }
    
    /// Get the world rotation of a body as a cosine/sine pair (complex number)
    func getRotation() -> B2Rot {
        b2Body_GetRotation(id)
    }
    
    /// Get the world transform of a body.
    func getTransform() -> B2Transform {
        b2Body_GetTransform(id)
    }
    
    /// Set the world transform of a body. This acts as a teleport and is fairly expensive.
    /// - note: Generally you should create a body with then intended transform.
    /// @see b2BodyDef::position and b2BodyDef::angle
    func setTransform(_ position: B2Vec2, _ rotation: B2Rot) {
        b2Body_SetTransform(id, position, rotation)
    }
    
    /// Get a local point on a body given a world point
    func getLocalPoint(_ worldPoint: B2Vec2) -> B2Vec2 {
        b2Body_GetLocalPoint(id, worldPoint)
    }
    
    /// Get a world point on a body given a local point
    func getWorldPoint(_ localPoint: B2Vec2) -> B2Vec2 {
        b2Body_GetWorldPoint(id, localPoint)
    }
    
    /// Get a local vector on a body given a world vector
    func getLocalVector(_ worldVector: B2Vec2) -> B2Vec2 {
        b2Body_GetLocalVector(id, worldVector)
    }
    
    /// Get a world vector on a body given a local vector
    func getWorldVector(_ localVector: B2Vec2) -> B2Vec2 {
        b2Body_GetWorldVector(id, localVector)
    }
    
    /// Set the velocity to reach the given transform after a given time step.
    /// The result will be close but maybe not exact. This is meant for kinematic bodies.
    /// This will automatically wake the body if asleep.
    func setTargetTransform(_ target: B2Transform, _ timeStep: Float) {
        b2Body_SetTargetTransform(id, target, timeStep)
    }
    
    /// Get the linear velocity of a local point attached to a body. Usually in meters per second.
    func getLocalPointVelocity(_ localPoint: B2Vec2) -> B2Vec2 {
        b2Body_GetLocalPointVelocity(id, localPoint)
    }
    
    /// Get the linear velocity of a world point attached to a body. Usually in meters per second.
    func getWorldPointVelocity(_ worldPoint: B2Vec2) -> B2Vec2 {
        b2Body_GetWorldPointVelocity(id, worldPoint)
    }
    
    /// Apply a force at a world point. If the force is not applied at the center of mass,
    /// it will generate a torque and affect the angular velocity. This optionally wakes up the body.
    /// The force is ignored if the body is not awake.
    /// - param bodyId: The body id
    /// - param force: The world force vector, usually in newtons (N)
    /// - param point: The world position of the point of application
    /// - param wake: Option to wake up the body
    func applyForce(_ force: B2Vec2, _ point: B2Vec2, _ wake: Bool) {
        b2Body_ApplyForce(id, force, point, wake)
    }
    
    /// Apply a force to the center of mass. This optionally wakes up the body.
    /// The force is ignored if the body is not awake.
    /// - param bodyId: The body id
    /// - param force: the world force vector, usually in newtons (N).
    /// - param wake: also wake up the body
    func applyForceToCenter(_ force: B2Vec2, _ wake: Bool) {
        b2Body_ApplyForceToCenter(id, force, wake)
    }
    
    /// Apply a torque. This affects the angular velocity without affecting the linear velocity.
    /// This optionally wakes the body. The torque is ignored if the body is not awake.
    /// - param bodyId: The body id
    /// - param torque: about the z-axis (out of the screen), usually in N*m.
    /// - param wake: also wake up the body
    func applyTorque(_ torque: Float, _ wake: Bool) {
        b2Body_ApplyTorque(id, torque, wake)
    }
    
    /// Apply an impulse at a point. This immediately modifies the velocity.
    /// It also modifies the angular velocity if the point of application
    /// is not at the center of mass. This optionally wakes the body.
    /// The impulse is ignored if the body is not awake.
    /// - param bodyId: The body id
    /// - param impulse: the world impulse vector, usually in N*s or kg*m/s.
    /// - param point: the world position of the point of application.
    /// - param wake: also wake up the body
    /// @warning This should be used for one-shot impulses. If you need a steady force,
    /// use a force instead, which will work better with the sub-stepping solver.
    func applyLinearImpulse(_ impulse: B2Vec2, _ point: B2Vec2, _ wake: Bool) {
        b2Body_ApplyLinearImpulse(id, impulse, point, wake)
    }
    
    /// Apply an impulse to the center of mass. This immediately modifies the velocity.
    /// The impulse is ignored if the body is not awake. This optionally wakes the body.
    /// - param bodyId: The body id
    /// - param impulse: the world impulse vector, usually in N*s or kg*m/s.
    /// - param wake: also wake up the body
    /// @warning This should be used for one-shot impulses. If you need a steady force,
    /// use a force instead, which will work better with the sub-stepping solver.
    func applyLinearImpulseToCenter(_ impulse: B2Vec2, _ wake: Bool) {
        b2Body_ApplyLinearImpulseToCenter(id, impulse, wake)
    }
    
    /// Apply an angular impulse. The impulse is ignored if the body is not awake.
    /// This optionally wakes the body.
    /// - param bodyId: The body id
    /// - param impulse: the angular impulse, usually in units of kg*m*m/s
    /// - param wake: also wake up the body
    /// @warning This should be used for one-shot impulses. If you need a steady force,
    /// use a force instead, which will work better with the sub-stepping solver.
    func applyAngularImpulse(_ impulse: Float, _ wake: Bool) {
        b2Body_ApplyAngularImpulse(id, impulse, wake)
    }
    
    /// Get the mass of the body, usually in kilograms
    func getMass() -> Float {
        b2Body_GetMass(id)
    }
    
    /// Get the rotational inertia of the body, usually in kg*m^2
    func getRotationalInertia() -> Float {
        b2Body_GetRotationalInertia(id)
    }
    
    /// Get the center of mass position of the body in local space
    func getLocalCenterOfMass() -> B2Vec2 {
        b2Body_GetLocalCenterOfMass(id)
    }
    
    /// Get the center of mass position of the body in world space
    func getWorldCenterOfMass() -> B2Vec2 {
        b2Body_GetWorldCenterOfMass(id)
    }
    
    /// This update the mass properties to the sum of the mass properties of the shapes.
    /// This normally does not need to be called unless you called SetMassData to override
    /// the mass and you later want to reset the mass.
    /// You may also use this when automatic mass computation has been disabled.
    /// You should call this regardless of body type.
    /// Note that sensor shapes may have mass.
    func applyMassFromShapes() {
        b2Body_ApplyMassFromShapes(id)
    }
    
    /// - returns: true if this body is awake
    func isAwake() -> Bool {
        b2Body_IsAwake(id)
    }
    
    /// Wake a body from sleep. This wakes the entire island the body is touching.
    /// @warning Putting a body to sleep will put the entire island of bodies touching this body to sleep,
    /// which can be expensive and possibly unintuitive.
    func setAwake(_ awake: Bool) {
        b2Body_SetAwake(id, awake)
    }
    
    /// Enable or disable sleeping for this body. If sleeping is disabled the body will wake.
    func enableSleep(_ enableSleep: Bool) {
        b2Body_EnableSleep(id, enableSleep)
    }
    
    /// Returns true if sleeping is enabled for this body
    func isSleepEnabled() -> Bool {
        b2Body_IsSleepEnabled(id)
    }
    
    /// Returns true if this body is enabled
    func isEnabled() -> Bool {
        b2Body_IsEnabled(id)
    }
    
    /// Disable a body by removing it completely from the simulation. This is expensive.
    func disable() {
        b2Body_Disable(id)
    }
    
    /// Enable a body by adding it to the simulation. This is expensive.
    func enable() {
        b2Body_Enable(id)
    }
    
    /// Set this body to have fixed rotation. This causes the mass to be reset in all cases.
    func setFixedRotation(_ flag: Bool) {
        b2Body_SetFixedRotation(id, flag)
    }
    
    /// Does this body have fixed rotation?
    func isFixedRotation() -> Bool {
        b2Body_IsFixedRotation(id)
    }
    
    /// Set this body to be a bullet. A bullet does continuous collision detection
    /// against dynamic bodies (but not other bullets).
    func setBullet(_ flag: Bool) {
        b2Body_SetBullet(id, flag)
    }
    
    /// Is this body a bullet?
    func isBullet() -> Bool {
        b2Body_IsBullet(id)
    }
    
    /// Enable/disable contact events on all shapes.
    /// @see b2ShapeDef::enableContactEvents
    /// @warning changing this at runtime may cause mismatched begin/end touch events
    func enableContactEvents(_ flag: Bool) {
        b2Body_EnableContactEvents(id, flag)
    }
    
    /// Enable/disable hit events on all shapes
    /// @see b2ShapeDef::enableHitEvents
    func enableHitEvents(_ flag: Bool) {
        b2Body_EnableHitEvents(id, flag)
    }
    
    /// Get the world that owns this body
    func getWorld() -> b2WorldId {
        b2Body_GetWorld(id)
    }
    
    /// Get the number of shapes on this body
    func getShapeCount() -> Int32 {
        b2Body_GetShapeCount(id)
    }
    
    /// Get the shape ids for all shapes on this body, up to the provided capacity.
    /// - returns:s the number of shape ids stored in the user array
    func getShapes(_ shapeArray: UnsafeMutablePointer<b2ShapeId>?, _ capacity: Int32) -> Int32 {
        b2Body_GetShapes(id, shapeArray, capacity)
    }
    
    /// Get the number of joints on this body
    func getJointCount() -> Int32 {
        b2Body_GetJointCount(id)
    }
    
    /// Get the joint ids for all joints on this body, up to the provided capacity
    /// - returns:s the number of joint ids stored in the user array
    func getJoints(_ jointArray: UnsafeMutablePointer<b2JointId>?, _ capacity: Int32) -> Int32 {
        b2Body_GetJoints(id, jointArray, capacity)
    }
    
    /// Get the maximum capacity required for retrieving all the touching contacts on a body
    func getContactCapacity() -> Int32 {
        b2Body_GetContactCapacity(id)
    }
    
    /// Get the touching contact data for a body.
    /// - note: Box2D uses speculative collision so some contact points may be separated.
    /// - returns:s the number of elements filled in the provided array
    /// @warning do not ignore the return value, it specifies the valid number of elements
    func getContactData(_ contactData: UnsafeMutablePointer<b2ContactData>?, _ capacity: Int32) -> Int32 {
        b2Body_GetContactData(id, contactData, capacity)
    }
    
    /// Get the current world AABB that contains all the attached shapes. Note that this may not encompass the body origin.
    /// If there are no shapes attached then the returned AABB is empty and centered on the body origin.
    func computeAABB() -> B2AABB {
        b2Body_ComputeAABB(id)
    }
    
    ///  Get the body type: static, kinematic, or dynamic
    /// Change the body type. This is an expensive operation. This automatically updates the mass
    /// properties regardless of the automatic mass setting.
    var type: B2BodyType {
        get {
            b2Body_GetType(id)
        }
        set(type) {
            b2Body_SetType(id, type)
        }
    }
    
    /// Get the linear velocity of a body's center of mass. Usually in meters per second.
    /// Set the linear velocity of a body. Usually in meters per second.
    var linearVelocity: B2Vec2 {
        get {
            b2Body_GetLinearVelocity(id)
        }
        set(linearVelocity) {
            b2Body_SetLinearVelocity(id, linearVelocity)
        }
    }
    
    /// Get the angular velocity of a body in radians per second
    /// Set the angular velocity of a body in radians per second
    var angularVelocity: Float {
        get {
            b2Body_GetAngularVelocity(id)
        }
        set(angularVelocity) {
            b2Body_SetAngularVelocity(id, angularVelocity)
        }
    }
    
    ///  Get the mass data for a body
    /// Override the body's mass properties. Normally this is computed automatically using the
    /// shape geometry and density. This information is lost if a shape is added or removed or if the
    /// body type changes.
    var massData: b2MassData {
        get {
            b2Body_GetMassData(id)
        }
        set(massData) {
            b2Body_SetMassData(id, massData)
        }
    }
    
    /// Get the current linear damping.
    /// Adjust the linear damping. Normally this is set in b2BodyDef before creation.
    var linearDamping: Float {
        get {
            b2Body_GetLinearDamping(id)
        }
        set(linearDamping) {
            b2Body_SetLinearDamping(id, linearDamping)
        }
    }
    
    /// Get the current angular damping.
    /// Adjust the angular damping. Normally this is set in b2BodyDef before creation.
    var angularDamping: Float {
        get {
            b2Body_GetAngularDamping(id)
        }
        set(angularDamping) {
            b2Body_SetAngularDamping(id, angularDamping)
        }
    }
    
    ///  Get the current gravity scale
    /// Adjust the gravity scale. Normally this is set in b2BodyDef before creation.
    /// @see b2BodyDef::gravityScale
    var gravityScale: Float {
        get {
            b2Body_GetGravityScale(id)
        }
        set(gravityScale) {
            b2Body_SetGravityScale(id, gravityScale)
        }
    }
    
    /// Get the sleep threshold, usually in meters per second.
    /// Set the sleep threshold, usually in meters per second
    var sleepThreshold: Float {
        get {
            b2Body_GetSleepThreshold(id)
        }
        set(sleepThreshold) {
            b2Body_SetSleepThreshold(id, sleepThreshold)
        }
    }
}
