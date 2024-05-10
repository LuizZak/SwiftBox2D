import box2d

class B2World {
    var id: b2WorldId

    init() {
        var worldDef = b2DefaultWorldDef()
        worldDef.workerCount = 1
        worldDef.enqueueTask = _enqueueTask
        worldDef.finishTask = _finishTask
        worldDef.enableSleep = true

        id = b2CreateWorld(&worldDef)
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
