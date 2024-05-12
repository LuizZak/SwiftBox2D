// HEADS UP!: Auto-generated file, changes made directly here will be overwritten by code generators.
// Generated by generate_types.py

import box2d

/// Body identifier validation. Provides validation for up to 64K allocations.
internal extension B2Body {
    /// Body identifier validation. Provides validation for up to 64K allocations.
    func isValid() -> Bool {
        b2Body_IsValid(id)
    }
    
    /// Get the body type: static, kinematic, or dynamic
    func getType() -> b2BodyType {
        b2Body_GetType(id)
    }
    
    /// Change the body type. This is an expensive operation. This automatically updates the mass
    /// properties regardless of the automatic mass setting.
    func setType(_ type: b2BodyType) {
        b2Body_SetType(id, type)
    }
    
    /// Set the user data for a body
    func setUserData(_ userData: UnsafeMutableRawPointer) {
        b2Body_SetUserData(id, userData)
    }
    
    /// Get the world position of a body. This is the location of the body origin.
    func getPosition() -> b2Vec2 {
        b2Body_GetPosition(id)
    }
    
    /// Get the world rotation of a body as a sine/cosine pair.
    func getRotation() -> b2Rot {
        b2Body_GetRotation(id)
    }
    
    /// Get the body angle in radians in the range [-pi, pi]
    func getAngle() -> Float {
        b2Body_GetAngle(id)
    }
    
    /// Get the world transform of a body.
    func getTransform() -> b2Transform {
        b2Body_GetTransform(id)
    }
    
    /// Set the world transform of a body. This acts as a teleport and is fairly expensive.
    func setTransform(_ position: b2Vec2, _ angle: Float) {
        b2Body_SetTransform(id, position, angle)
    }
    
    /// Get a local point on a body given a world point
    func getLocalPoint(_ worldPoint: b2Vec2) -> b2Vec2 {
        b2Body_GetLocalPoint(id, worldPoint)
    }
    
    /// Get a world point on a body given a local point
    func getWorldPoint(_ localPoint: b2Vec2) -> b2Vec2 {
        b2Body_GetWorldPoint(id, localPoint)
    }
    
    /// Get a local vector on a body given a world vector
    func getLocalVector(_ worldVector: b2Vec2) -> b2Vec2 {
        b2Body_GetLocalVector(id, worldVector)
    }
    
    /// Get a world vector on a body given a local vector
    func getWorldVector(_ localVector: b2Vec2) -> b2Vec2 {
        b2Body_GetWorldVector(id, localVector)
    }
    
    /// Get the linear velocity of a body's center of mass
    func getLinearVelocity() -> b2Vec2 {
        b2Body_GetLinearVelocity(id)
    }
    
    /// Get the angular velocity of a body in radians per second
    func getAngularVelocity() -> Float {
        b2Body_GetAngularVelocity(id)
    }
    
    /// Set the linear velocity of a body
    func setLinearVelocity(_ linearVelocity: b2Vec2) {
        b2Body_SetLinearVelocity(id, linearVelocity)
    }
    
    /// Set the angular velocity of a body in radians per second
    func setAngularVelocity(_ angularVelocity: Float) {
        b2Body_SetAngularVelocity(id, angularVelocity)
    }
    
    /// Apply a force at a world point. If the force is not
    /// applied at the center of mass, it will generate a torque and
    /// affect the angular velocity. This wakes up the body.
    /// @param force the world force vector, usually in Newtons (N).
    /// @param point the world position of the point of application.
    /// @param wake also wake up the body
    func applyForce(_ force: b2Vec2, _ point: b2Vec2, _ wake: Bool) {
        b2Body_ApplyForce(id, force, point, wake)
    }
    
    /// Apply a force to the center of mass. This wakes up the body.
    /// @param force the world force vector, usually in Newtons (N).
    /// @param wake also wake up the body
    func applyForceToCenter(_ force: b2Vec2, _ wake: Bool) {
        b2Body_ApplyForceToCenter(id, force, wake)
    }
    
    /// Apply a torque. This affects the angular velocity
    /// without affecting the linear velocity of the center of mass.
    /// @param torque about the z-axis (out of the screen), usually in N-m.
    /// @param wake also wake up the body
    func applyTorque(_ torque: Float, _ wake: Bool) {
        b2Body_ApplyTorque(id, torque, wake)
    }
    
    /// Apply an impulse at a point. This immediately modifies the velocity.
    /// It also modifies the angular velocity if the point of application
    /// is not at the center of mass. This wakes up the body.
    /// This should be used for one-shot impulses. If you need a steady force,
    /// use a force instead, which will work better with the sub-stepping solver.
    /// @param impulse the world impulse vector, usually in N-seconds or kg-m/s.
    /// @param point the world position of the point of application.
    /// @param wake also wake up the body
    func applyLinearImpulse(_ impulse: b2Vec2, _ point: b2Vec2, _ wake: Bool) {
        b2Body_ApplyLinearImpulse(id, impulse, point, wake)
    }
    
    /// Apply an impulse to the center of mass. This immediately modifies the velocity.
    /// This should be used for one-shot impulses. If you need a steady force,
    /// use a force instead, which will work better with the sub-stepping solver.
    /// @param impulse the world impulse vector, usually in N-seconds or kg-m/s.
    /// @param wake also wake up the body
    func applyLinearImpulseToCenter(_ impulse: b2Vec2, _ wake: Bool) {
        b2Body_ApplyLinearImpulseToCenter(id, impulse, wake)
    }
    
    /// Apply an angular impulse.
    /// This should be used for one-shot impulses. If you need a steady force,
    /// use a force instead, which will work better with the sub-stepping solver.
    /// @param impulse the angular impulse in units of
    /// kg*m*m/s
    /// @param wake also wake up the body
    func applyAngularImpulse(_ impulse: Float, _ wake: Bool) {
        b2Body_ApplyAngularImpulse(id, impulse, wake)
    }
    
    /// Get the mass of the body (kilograms)
    func getMass() -> Float {
        b2Body_GetMass(id)
    }
    
    /// Get the inertia tensor of the body. In 2D this is a single number. (kilograms * meters^2)
    func getInertiaTensor() -> Float {
        b2Body_GetInertiaTensor(id)
    }
    
    /// Get the center of mass position of the body in local space.
    func getLocalCenterOfMass() -> b2Vec2 {
        b2Body_GetLocalCenterOfMass(id)
    }
    
    /// Get the center of mass position of the body in world space.
    func getWorldCenterOfMass() -> b2Vec2 {
        b2Body_GetWorldCenterOfMass(id)
    }
    
    /// Override the body's mass properties. Normally this is computed automatically using the
    /// shape geometry and density. This information is lost if a shape is added or removed or if the
    /// body type changes.
    func setMassData(_ massData: b2MassData) {
        b2Body_SetMassData(id, massData)
    }
    
    /// Get the mass data for a body.
    func getMassData() -> b2MassData {
        b2Body_GetMassData(id)
    }
    
    /// This resets the mass properties to the sum of the mass properties of the shapes.
    /// This normally does not need to be called unless you called SetMassData to override
    /// the mass and you later want to reset the mass.
    /// You may also use this when automatic mass computation has been disabled.
    /// You should call this regardless of body type.
    func applyMassFromShapes() {
        b2Body_ApplyMassFromShapes(id)
    }
    
    /// Set the automatic mass setting.
    func setAutomaticMass(_ automaticMass: Bool) {
        b2Body_SetAutomaticMass(id, automaticMass)
    }
    
    /// Get the automatic mass setting.
    func getAutomaticMass() -> Bool {
        b2Body_GetAutomaticMass(id)
    }
    
    /// Adjust the linear damping. Normally this is set in b2BodyDef before creation.
    func setLinearDamping(_ linearDamping: Float) {
        b2Body_SetLinearDamping(id, linearDamping)
    }
    
    /// Get the current linear damping.
    func getLinearDamping() -> Float {
        b2Body_GetLinearDamping(id)
    }
    
    /// Adjust the angular damping. Normally this is set in b2BodyDef before creation.
    func setAngularDamping(_ angularDamping: Float) {
        b2Body_SetAngularDamping(id, angularDamping)
    }
    
    /// Get the current angular damping.
    func getAngularDamping() -> Float {
        b2Body_GetAngularDamping(id)
    }
    
    /// Adjust the gravity scale. Normally this is set in b2BodyDef before creation.
    func setGravityScale(_ gravityScale: Float) {
        b2Body_SetGravityScale(id, gravityScale)
    }
    
    /// Get the current gravity scale.
    func getGravityScale() -> Float {
        b2Body_GetGravityScale(id)
    }
    
    /// Is this body awake?
    func isAwake() -> Bool {
        b2Body_IsAwake(id)
    }
    
    /// Wake a body from sleep. This wakes the entire island the body is touching.
    /// Putting a body to sleep will put the entire island of bodies touching this body to sleep,
    /// which can be expensive.
    func setAwake(_ awake: Bool) {
        b2Body_SetAwake(id, awake)
    }
    
    /// Enable or disable sleeping this body. If sleeping is disabled the body will wake.
    func enableSleep(_ enableSleep: Bool) {
        b2Body_EnableSleep(id, enableSleep)
    }
    
    /// @return is sleeping enabled for this body?
    func isSleepEnabled() -> Bool {
        b2Body_IsSleepEnabled(id)
    }
    
    /// Set the sleep threshold. Normally in meters per second.
    func setSleepThreshold(_ sleepVelocity: Float) {
        b2Body_SetSleepThreshold(id, sleepVelocity)
    }
    
    /// Get the sleep threshold. Normally in meters per second.
    func getSleepThreshold() -> Float {
        b2Body_GetSleepThreshold(id)
    }
    
    /// Is this body enabled?
    func isEnabled() -> Bool {
        b2Body_IsEnabled(id)
    }
    
    /// Disable a body by removing it completely from the simulation
    func disable() {
        b2Body_Disable(id)
    }
    
    /// Enable a body by adding it to the simulation
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
    
    /// Enable/disable hit events on all shapes.
    func enableHitEvents(_ enableHitEvents: Bool) {
        b2Body_EnableHitEvents(id, enableHitEvents)
    }
    
    /// Get the number of shapes on this body
    func getShapeCount() -> Int32 {
        b2Body_GetShapeCount(id)
    }
    
    /// Get the shape ids for all shapes on this body, up to the provided capacity.
    /// @returns the number of shape ids stored in the user array
    func getShapes(_ shapeArray: UnsafeMutablePointer<b2ShapeId>, _ capacity: Int32) -> Int32 {
        b2Body_GetShapes(id, shapeArray, capacity)
    }
    
    /// Get the number of joints on this body
    func getJointCount() -> Int32 {
        b2Body_GetJointCount(id)
    }
    
    /// Get the joint ids for all joints on this body, up to the provided capacity
    /// @returns the number of joint ids stored in the user array
    func getJoints(_ jointArray: UnsafeMutablePointer<b2JointId>, _ capacity: Int32) -> Int32 {
        b2Body_GetJoints(id, jointArray, capacity)
    }
    
    /// Get the maximum capacity required for retrieving all the touching contacts on a body
    func getContactCapacity() -> Int32 {
        b2Body_GetContactCapacity(id)
    }
    
    /// Get the touching contact data for a body
    func getContactData(_ contactData: UnsafeMutablePointer<b2ContactData>, _ capacity: Int32) -> Int32 {
        b2Body_GetContactData(id, contactData, capacity)
    }
    
    /// Get the current world AABB that contains all the attached shapes. Note that this may not emcompass the body origin.
    /// If there are no shapes attached then the returned AABB is empty and centered on the body origin.
    func computeAABB() -> b2AABB {
        b2Body_ComputeAABB(id)
    }
}
