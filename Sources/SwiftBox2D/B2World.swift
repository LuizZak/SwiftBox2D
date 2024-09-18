import box2d

public class B2World {
    var id: b2WorldId

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

    public func step(_ timeStep: Float, subSteps: Int = 4) {
        b2World_Step(id, timeStep, Int32(subSteps))
    }
}

private func _enqueueTask(_ task: (@convention(c) (Int32, Int32, UInt32, UnsafeMutableRawPointer?) -> Void)?, itemCount: Int32, minRange: Int32, taskContext: UnsafeMutableRawPointer?, userContext: UnsafeMutableRawPointer?) -> UnsafeMutableRawPointer? {
    task?(0, itemCount, 0, taskContext)

    return nil
}

private func _finishTask(_ task: UnsafeMutableRawPointer?, _ userContext: UnsafeMutableRawPointer?) {

}
