import Foundation
import CoreGraphics
import SwiftBox2D
import simd

var renderingScale: B2Vec2 = B2Vec2(x: 1, y: 1)
var renderingOffset: B2Vec2 = B2Vec2(x: 0, y: 0)

extension B2Vec2 {
    typealias NativeMatrixType = Matrix3x3
    
    /// Helper post-fix alias for global function `toWorldCoords(self)`
    var inWorldCoords: B2Vec2 {
        return (self - renderingOffset) / renderingScale
    }

    /// Helper post-fix alias for global function `toScreenCoords(self)`
    var inScreenCoords: B2Vec2 {
        return self * renderingScale + renderingOffset
    }
}

protocol DemoSceneDelegate: AnyObject {
    func didUpdatePhysicsTimer(intervalCount: Int,
                               timeMilliRounded: TimeInterval,
                               fps: TimeInterval,
                               avgMilliRounded: TimeInterval)
    func didUpdateRenderTimer(timeMilliRounded: TimeInterval, fps: TimeInterval)
}

class DemoScene {
    weak var delegate: DemoSceneDelegate?
    
    var boundsSize: CGSize
    
    var sizeAsPoint: B2Vec2 {
        B2Vec2(x: Float(boundsSize.width), y: Float(boundsSize.height))
    }
    
    /// Main OpenGL VAO in which all bodies will be rendered on
    var vertexBuffer: VertexBuffer
    
    var updateLabelStopwatch = Stopwatch(startTime: 0)
    var renderLabelStopwatch = Stopwatch(startTime: 0)
    var intervals: [CFAbsoluteTime] = []
    
    let baseRenderingScale = B2Vec2(x: 20.0, y: 20.0)
    
    let labelUpdateInterval = 0.5
    
    var inputMode = InputMode.dragBody
    
    var timeSinceLastJump: Double = .infinity
    
    // The location of the user's finger, in physics world coordinates
    var pointerLocation = B2Vec2.zero
    var keyMap: KeyMap = .init()
    
    /// Whether to perform a detailed render of the scene. Detailed rendering
    /// renders, along with the body shape, the body's normals, global shape and
    /// axis, and collision normals
    var useDetailedRender = true
    
    var dragInfo: DragInfo?
    var dragForce: Float = 100.0
    
    var rayCastBody: RayCastBody?
    
    var world: B2World!
    
    init(boundsSize: CGSize, delegate: DemoSceneDelegate?) {
        self.boundsSize = boundsSize
        self.delegate = delegate
        vertexBuffer = VertexBuffer()
        renderingOffset = sizeAsPoint / 2
        renderingScale = baseRenderingScale
    }
    
    func update(timeSinceLastFrame: TimeInterval) {
        let sw = Stopwatch()
        
        updateWithTimeSinceLastUpdate(timeSinceLastFrame)
        
        let time = sw.stop() * 1000
        
        intervals.append(time)
        while intervals.count > 200 {
            intervals.removeFirst()
        }
        
        if let duration = updateLabelStopwatch.duration, duration > labelUpdateInterval {
            updateLabelStopwatch.reset()
            
            let timeMilli = time
            let timeMilliRounded = round(timeMilli * 100) / 100
            let fps = 1000 / timeMilliRounded
            
            let avgMilli = intervals.reduce(0, +) / CFAbsoluteTime(intervals.count)
            let avgMilliRounded = round(avgMilli * 100) / 100
            
            DispatchQueue.main.async {
                self.delegate?.didUpdatePhysicsTimer(intervalCount: self.intervals.count,
                                                     timeMilliRounded: timeMilliRounded,
                                                     fps: fps,
                                                     avgMilliRounded: avgMilliRounded)
            }
        }
    }
    
    func renderToVaoBuffer() {
        vertexBuffer.clearVertices()
        
        let sw = Stopwatch.startNew()
        
        if useDetailedRender {
            
        }
        
        drawWorld()
        
        rayCastBody?.draw(in: self)
        
        // Adjust viewport by the aspect ratio
        let viewportMatrix = matrixForOrthoProjection(width: Float(boundsSize.width), height: Float(boundsSize.height))
        
        // Matrix to transform SwiftBox2D's coordinates into proper coordinates
        // for OpenGL
        let mat = B2Vec2.matrix(scalingBy: renderingScale, rotatingBy: 0, translatingBy: renderingOffset)
        
        // Convert point to screen coordinates
        let screenMatrix = mat * viewportMatrix
        vertexBuffer.applyTransformation(screenMatrix.matrix3x3())
        
        if let duration = renderLabelStopwatch.duration, duration > labelUpdateInterval {
            renderLabelStopwatch.reset()
            
            let time = round(sw.stop() * 1000 * 20) / 20
            let fps = 1000 / time
            
            delegate?.didUpdateRenderTimer(timeMilliRounded: time, fps: fps)
        }
    }
    
    func updateWithTimeSinceLastUpdate(_ timeSinceLast: CFTimeInterval) {
        timeSinceLastJump += timeSinceLast
        
        if let dragInfo {
            dragInfo.mouseDragBody.setTargetTransform(.init(p: pointerLocation, q: .identity), 1 / 60.0, true)
        }
        
        if let rayCastBody {
            let moveForce: Float = 400.0
            var moveVector: B2Vec2 = .zero
            if keyMap.isKeyDown(.a) {
                moveVector.x += -1
            }
            if keyMap.isKeyDown(.d) {
                moveVector.x += 1
            }
            if keyMap.isKeyDown(.w) {
                moveVector.y += 1
            }
            if keyMap.isKeyDown(.s) {
                moveVector.y += -1
            }
            
            rayCastBody.update(world: world, timeStep: 1 / 60.0)
            
            if moveVector != .zero {
                rayCastBody.cullJoints(headingVector: moveVector)
            }
            
            if keyMap.isKeyDown(.a) {
                rayCastBody.body.applyForceToCenter(B2Vec2(x: -moveForce, y: 0), true)
            }
            if keyMap.isKeyDown(.d) {
                rayCastBody.body.applyForceToCenter(B2Vec2(x: moveForce, y: 0), true)
            }
            if keyMap.isKeyDown(.w) && rayCastBody.jointCount() > 2 {
                rayCastBody.body.applyForceToCenter(B2Vec2(x: 0, y: moveForce), true)
            }
            if keyMap.isKeyDown(.s) && rayCastBody.jointCount() > 2 {
                rayCastBody.body.applyForceToCenter(B2Vec2(x: 0, y: -moveForce), true)
            }
            
            if let time = keyMap.keyHeldTime(.space), time == 0.0 {
                if timeSinceLastJump > 0.016 && rayCastBody.jointCount() >= 2 {
                    let angleVec = B2Vec2.fromAngle(rayCastBody.averageAngle())
                    
                    timeSinceLastJump = 0.0
                    
                    let jumpForce: Float = 100.0
                    rayCastBody.body.applyLinearImpulseToCenter(-angleVec * jumpForce, true)
                }
            }
            
            if timeSinceLastJump <= 0.1 {
                rayCastBody.cullAllJoints()
            }
            
            if rayCastBody.jointCount() > 1 {
                let angle = rayCastBody.averageAngle()
                
                let torque = calculateTorsionSpringTorque(
                    angle: rayCastBody.body.getRotation().angle, angularMomentum: rayCastBody.body.angularVelocity,
                    targetAngle: angle, targetAngularMomentum: 0.0,
                    springK: 800.0,
                    springD: 80.0
                )
                
                rayCastBody.body.applyTorque(torque, true)
            }
        }
        
        // Update the physics world
        world.step(1 / 60.0, 4)
        
        keyMap.update(deltaTime: timeSinceLast)
    }
    
    /// Enum used to modify the input mode of the test simulation
    enum InputMode: Int {
        /// Creates a jiggly ball under the finger on tap
        case createBall
        /// Allows dragging bodies around
        case dragBody
    }
    
    struct DragInfo {
        let mouseDragBody: B2Body
        let mouseDragJoint: B2Joint
    }
}

// MARK: - Input
extension DemoScene {
    func touchDown(at screenPoint: B2Vec2) {
        let worldPoint = screenPoint.inWorldCoords
        
        let tolerance: B2Vec2 = .init(x: 0.01, y: 0.01)
        let aabb = B2AABB(lowerBound: worldPoint - tolerance, upperBound: worldPoint + tolerance)
        
        var hitBody: B2Body?
        world.overlapAABB(aabb, filter: .default()) { shape in
            let body = B2Body(id: shape.getBody())
            if body.type != .b2DynamicBody {
                return true
            }
            
            if shape.testPoint(worldPoint) {
                hitBody = body
                return false
            }
            
            return true
        }
        
        if let hitBody {
            var bodyDef = b2BodyDef.default()
            bodyDef.type = .b2KinematicBody
            bodyDef.position = worldPoint
            bodyDef.enableSleep = false
            
            let mouseBody = world.createBody(bodyDef)
            
            var jointDef = b2MotorJointDef.default()
            jointDef.base.bodyIdA = mouseBody.id
            jointDef.base.bodyIdB = hitBody.id
            jointDef.base.localFrameB.p = hitBody.getLocalPoint(worldPoint)
            jointDef.linearHertz = 7.5
            jointDef.linearDampingRatio = 1.0
            
            let massData = hitBody.massData
            let g = world.gravity.length
            let mg = massData.mass * g
            
            jointDef.maxSpringForce = dragForce * mg
            
            if massData.mass > 0.0 {
                // This acts like angular friction
                let lever = (massData.rotationalInertia / massData.mass).squareRoot()
                jointDef.maxVelocityTorque = 0.25 * lever * mg
            }
            
            let mouseJoint = world.createJoint(jointDef)
            
            dragInfo = .init(mouseDragBody: mouseBody, mouseDragJoint: mouseJoint)
        }
    }
    
    func touchMoved(at screenPoint: B2Vec2) {
        let worldPoint = screenPoint.inWorldCoords
        
        pointerLocation = worldPoint
    }
    
    func touchEnded(at screenPoint: B2Vec2) {
        // Reset dragging point
        if let dragInfo {
            dragInfo.mouseDragJoint.destroy(wakeAttached: true)
            dragInfo.mouseDragBody.destroy()
            self.dragInfo = nil
        }
    }
    
    func onKeyDown(keyCode: KeyCode) {
        keyMap.setKeyDown(keyCode)
    }
    
    func onKeyUp(keyCode: KeyCode) {
        keyMap.setKeyUp(keyCode)
    }
}

extension DemoScene {
    func initializeLevel() {
        let worldDef = b2WorldDef.default()
        world = B2World(worldDef)
        
        let circleBody = createCenterCircle()
        rayCastBody = RayCastBody(body: circleBody)
        
        createSideBoxes()
        createConnectedBalls()
        createTumblerCircle()
    }
    
    func createSideBoxes() {
        createBox(
            center: (sizeAsPoint * B2Vec2(x: 0, y: 0)).inWorldCoords,
            size: (sizeAsPoint * B2Vec2(x: 2, y: 0.1)) / renderingScale.absolute
        )
        createBox(
            center: (sizeAsPoint * B2Vec2(x: 0, y: 0)).inWorldCoords,
            size: (sizeAsPoint * B2Vec2(x: 0.1, y: 2)) / renderingScale.absolute
        )
        createBox(
            center: (sizeAsPoint * B2Vec2(x: 1, y: 0)).inWorldCoords,
            size: (sizeAsPoint * B2Vec2(x: 0.1, y: 2)) / renderingScale.absolute
        )
        createBox(
            center: (sizeAsPoint * B2Vec2(x: 0, y: 1)).inWorldCoords,
            size: (sizeAsPoint * B2Vec2(x: 2, y: 0.1)) / renderingScale.absolute
        )
    }
    
    @discardableResult
    func createCenterCircle() -> B2Body {
        var bodyDef = b2BodyDef.default()
        bodyDef.type = .b2DynamicBody
        bodyDef.position = (sizeAsPoint / 3.0).inWorldCoords
        bodyDef.angularDamping = 0.9
        bodyDef.rotation = B2Rot(fromRadians: 0.0)
        
        let circle = B2Circle(center: .zero, radius: 1.5)
        
        let body = world.createBody(bodyDef)
        body.createShape(circle, shapeDef: .default())
        
        return body
    }
    
    func createConnectedBalls() {
        var bodyDef = b2BodyDef.default()
        bodyDef.type = .b2DynamicBody
        
        let circle = B2Circle(center: .zero, radius: 1.0)
        
        bodyDef.position = (sizeAsPoint * B2Vec2(x: 0.1, y: 0.5)).inWorldCoords
        let body1 = world.createBody(bodyDef)
        body1.createShape(circle, shapeDef: .default())
        
        bodyDef.position = (sizeAsPoint * B2Vec2(x: 0.3, y: 0.5)).inWorldCoords
        let body2 = world.createBody(bodyDef)
        body2.createShape(circle, shapeDef: .default())
        
        var jointDef = b2DistanceJointDef.default()
        jointDef.bodyA = body1
        jointDef.bodyB = body2
        jointDef.length = body1.getPosition().distance(to: body2.getPosition())
        world.createJoint(jointDef)
    }
    
    func createTumblerCircle() {
        var bodyDef = b2BodyDef.default()
        bodyDef.type = .b2DynamicBody
        bodyDef.position = (sizeAsPoint * B2Vec2(x: 0.5, y: 0.5)).inWorldCoords
        
        var pinBodyDef = b2BodyDef.default()
        pinBodyDef.position = bodyDef.position
        
        let circle = B2Circle(center: .zero, radius: 3.0)
        
        let pinBody = world.createBody(pinBodyDef)
        pinBody.createShape(B2Circle(center: .zero, radius: 0.1), shapeDef: .default())
        
        let circleBody = world.createBody(bodyDef)
        circleBody.createShape(circle, shapeDef: .default())
        
        var pinJointDef = b2RevoluteJointDef.default()
        pinJointDef.bodyA = circleBody
        pinJointDef.bodyB = pinBody
        pinJointDef.motorSpeed = 16.0
        pinJointDef.maxMotorTorque = 8000.0
        pinJointDef.enableMotor = true
        
        world.createJoint(pinJointDef)
    }
    
    @discardableResult
    func createBox(center: B2Vec2, size: B2Vec2) -> B2Body {
        var bodyDef = b2BodyDef.default()
        bodyDef.position = center
        
        let polygon = B2Polygon.makeBox(halfWidth: size.x / 2, halfHeight: size.y / 2)
        
        let body = world.createBody(bodyDef)
        body.createShape(polygon, shapeDef: .default())
        
        return body
    }
}

// MARK: - Rendering
extension DemoScene {
    ///                                               1
    /// Returns a 3x3 matrix for projecting onto a -1 0 1 -style space such that
    ///                                              -1
    /// a [0, 0] vector projects into the top-left (1, -1), and [width, height]
    /// projects into the bottom-right (-1, 1).
    ///
    func matrixForOrthoProjection(width: Float, height: Float) -> B2Vec2.NativeMatrixType {
        let size = B2Vec2(x: width, y: height)
        let scaledSize = B2Vec2(x: 1 / width, y: 1 / height) * 2
        
        let matrix = B2Vec2.matrix(translatingBy: -size / 2)
        return matrix * B2Vec2.matrix(scalingBy: scaledSize)
    }
    
    func drawWorld() {
        var debugDraw = b2DebugDraw.default()
        
        debugDraw.context = Unmanaged.passUnretained(self).toOpaque()
        // Circles
        debugDraw.DrawCircleFcn = { (position, radius, color, ptr) in
            let demoScene = Unmanaged<DemoScene>.fromOpaque(ptr!).takeUnretainedValue()
            
            demoScene.drawCircle(center: position, radius: radius, color: color.toUInt)
        }
        // Solid circles
        debugDraw.DrawSolidCircleFcn = { (transform, radius, color, ptr) in
            let demoScene = Unmanaged<DemoScene>.fromOpaque(ptr!).takeUnretainedValue()
            
            let centerStart = transform.p
            let centerEnd = centerStart + B2Vec2(x: 1, y: 0).rotated(by: transform.q) * radius
            
            demoScene.drawCircle(center: transform.p, radius: radius, color: color.toUInt)
            demoScene.drawLine(from: centerStart, to: centerEnd, color: invertColor(color.toUInt))
        }
        // Polygons
        debugDraw.DrawPolygonFcn = { (vertices: UnsafePointer<B2Vec2>?, vertexCount: Int32, color, ptr) in
            let buffer = UnsafeBufferPointer(start: vertices!, count: Int(vertexCount))
            let demoScene = Unmanaged<DemoScene>.fromOpaque(ptr!).takeUnretainedValue()
            
            demoScene.drawPolyOutline(Array(buffer), color: color.toUInt, width: 1)
        }
        // Solid polygons
        debugDraw.DrawSolidPolygonFcn = { (transform, vertices, vertexCount, radius, color, ptr) in
            let buffer = UnsafeBufferPointer(start: vertices!, count: Int(vertexCount))
            let demoScene = Unmanaged<DemoScene>.fromOpaque(ptr!).takeUnretainedValue()
            
            var transformed: [B2Vec2] = []
            
            for point in buffer {
                let modified = transform * point
                transformed.append(modified)
            }
            
            demoScene.drawPolyFilled(transformed, color: color.toUInt)
        }
        // Lines
        debugDraw.DrawLineFcn = { (p1, p2, color, ptr) in
            let demoScene = Unmanaged<DemoScene>.fromOpaque(ptr!).takeUnretainedValue()
            
            demoScene.drawLine(from: p1, to: p2, color: color.toUInt)
        }
        // Point
        debugDraw.DrawPointFcn = { (p, size, color, ptr) in
            let demoScene = Unmanaged<DemoScene>.fromOpaque(ptr!).takeUnretainedValue()
            
            demoScene.drawCircle(center: p, radius: size * 0.01, sides: 6, color: color.toUInt)
        }
        // Transforms
        debugDraw.DrawTransformFcn = { (transform, ptr) in
            let demoScene = Unmanaged<DemoScene>.fromOpaque(ptr!).takeUnretainedValue()
            
            let origin = b2TransformPoint(transform, B2Vec2.zero)
            let up = B2Vec2(x: 0, y: 1).rotated(by: transform.q)
            let right = B2Vec2(x: 1, y: 0).rotated(by: transform.q)
            
            demoScene.drawLine(from: origin, to: origin + up, color: 0xFF00FF00)
            demoScene.drawLine(from: origin, to: origin + right, color: 0xFFFF0000)
        }
        
        debugDraw.drawBounds = true
        debugDraw.drawJoints = true
        debugDraw.drawShapes = true
        debugDraw.drawContactPoints = true
        debugDraw.drawMass = true
        
        world.draw(&debugDraw)
    }
    
    func drawLine(from start: B2Vec2, to end: B2Vec2, color: UInt = 0xFFFFFFFF, width: Float = 0.5) {
        let normal = ((start - end).normalized.leftPerpendicular() / 15) * width
        
        let i0 = vertexBuffer.addVertex(start + normal, color: color)
        let i1 = vertexBuffer.addVertex(end + normal, color: color)
        let i2 = vertexBuffer.addVertex(end - normal, color: color)
        let i3 = vertexBuffer.addVertex(start - normal, color: color)
        
        vertexBuffer.addTriangleWithIndices(i0, i1, i2)
        vertexBuffer.addTriangleWithIndices(i2, i3, i0)
        
        // Draw a pointy line to make the line look less squared
        let p0 = vertexBuffer.addVertex(start - normal.leftPerpendicular(), color: color)
        let p1 = vertexBuffer.addVertex(end + normal.leftPerpendicular(), color: color)
        
        vertexBuffer.addTriangleWithIndices(i0, p0, i1)
        vertexBuffer.addTriangleWithIndices(i2, p1, i3)
    }
    
    func drawCircle(center point: B2Vec2, radius: Float, sides: Int = 40, color: UInt = 0xFFFFFFFF) {
        let prevColor = vertexBuffer.currentColor
        vertexBuffer.currentColor = color
        defer {
            vertexBuffer.currentColor = prevColor
        }
        
        // Add triangles that connect the edges to a center vertex to form the
        // circle
        let center = vertexBuffer.addVertex(point)
        
        for i in 0..<sides {
            let angle = (Float(i) / Float(sides)) * (Float.pi * 2.0)
            let vertex = point + B2Vec2(x: cos(angle), y: sin(angle)) * radius
            
            vertexBuffer.addVertex(x: vertex.x, y: vertex.y)
        }
        
        for vert in 0..<sides {
            let next = (vert + 1) % sides
            
            vertexBuffer.addTriangleWithIndices(center + UInt32(vert) + 1,
                                                center + UInt32(next) + 1,
                                                center)
        }
    }
    
    func drawPolyOutline(_ points: [B2Vec2], color: UInt = 0xFFFFFFFF, width: Float = 0.5) {
        guard var last = points.last else {
            return
        }
        
        for point in points {
            drawLine(from: point, to: last, color: color, width: width)
            last = point
        }
    }
    
    func drawPolyFilled(_ points: [B2Vec2], color: UInt = 0xFFFFFFFF) {
        // Triangulate body's polygon
        guard let (vertices, indices) = LibTessTriangulate.process(polygon: points) else {
            return
        }
        
        let start = UInt32(vertexBuffer.vertices.count)
        
        let prev = vertexBuffer.currentColor
        vertexBuffer.currentColor = color
        
        for vert in vertices {
            vertexBuffer.addVertex(x: vert.x, y: vert.y)
        }
        
        vertexBuffer.currentColor = prev
        
        // Add vertex index triplets
        for i in 0..<indices.count / 3 {
            vertexBuffer.addTriangleWithIndices(start + UInt32(indices[i * 3]),
                                                start + UInt32(indices[i * 3 + 1]),
                                                start + UInt32(indices[i * 3 + 2]))
        }
    }
}

extension B2Vec2.NativeMatrixType {
    /// Returns a 4x4 floating-point transformation matrix for this matrix
    /// object
    func matrix4x4() -> float4x4 {
        var matrix = float4x4(diagonal: [1, 1, 1, 1])
        
        matrix[0] = .init(x: Float(self[0, 0]), y: Float(self[0, 1]), z: 0, w: Float(self[0, 2]))
        matrix[1] = .init(x: Float(self[1, 0]), y: Float(self[1, 1]), z: 0, w: Float(self[1, 2]))
        matrix[2] = .init(x: Float(self[2, 0]), y: Float(self[2, 1]), z: 1, w: Float(self[2, 2]))
        matrix[3] = .init(x: 0, y: 0, z: 0, w: 1)
        
        return matrix
    }
    
    /// Returns a 3x3 floating-point transformation matrix for this matrix
    /// object
    func matrix3x3() -> float3x3 {
        var matrix = float3x3(diagonal: [1, 1, 1])
        
        matrix[0] = .init(x: Float(self[0, 0]), y: Float(self[0, 1]), z: Float(self[0, 2]))
        matrix[1] = .init(x: Float(self[1, 0]), y: Float(self[1, 1]), z: Float(self[1, 2]))
        matrix[2] = .init(x: Float(self[2, 0]), y: Float(self[2, 1]), z: Float(self[2, 2]))
        
        return matrix
    }
}

class RayCastBody {
    let body: B2Body
    var rayJoints: [RayJointPair] = []
    var latestRayCasts: [RayCastResult] = []
    
    init(body: B2Body) {
        self.body = body
        _generateRayJoints()
    }
    
    private func _generateRayJoints() {
        rayJoints = []
        
        let rayCount = 64
        let rayLength: Float = 4.0
        
        let startAngle: Float = 0.0
        let endAngle: Float = .pi * 2.0
        
        for i in 0..<rayCount {
            let fraction = Float(i) / Float(rayCount)
            let angle = startAngle + fraction * (endAngle - startAngle)
            
            let rayJoint = RayJointPair(body: body, rayLength: rayLength, angle: B2Rot(fromRadians: angle))
            rayJoints.append(rayJoint)
        }
    }
    
    func update(world: B2World, timeStep: Float) {
        latestRayCasts = []
        
        let origin = body.getPosition()
        
        for rayJoint in rayJoints {
            if let result = rayJoint.update(world: world, origin: origin, ignore: [body]) {
                latestRayCasts.append(result)
            }
        }
    }
    
    func cullAllJoints() {
        for rayJoint in rayJoints {
            rayJoint.detachJoint()
        }
    }
    
    func cullJoints(headingVector: B2Vec2) {
        guard headingVector.length >= 0.001 else {
            return
        }
        
        for rayJoint in rayJoints {
            let dot = rayJoint.rayTranslation.dot(headingVector)
            if dot < 0 {
                rayJoint.detachJoint()
            }
        }
    }
    
    func jointCount() -> Int {
        var result = 0
        
        for rayJoint in rayJoints {
            if rayJoint.isAttached() {
                result += 1
            }
        }
        
        return result
    }
    
    func averageAngle() -> Float {
        var sum: B2Vec2 = .zero
        
        for rayJoint in rayJoints {
            if rayJoint.isAttached() {
                sum += rayJoint.rayTranslation.normalized
            }
        }
        
        return sum.angle
    }
    
    func draw(in demoScene: DemoScene) {
        for latestRayCast in latestRayCasts {
            demoScene.drawLine(from: latestRayCast.origin, to: latestRayCast.point, color: 0xFFFF0000, width: 1.0)
        }
    }
}

private extension B2HexColor {
    var toUInt: UInt {
        UInt(rawValue) | 0xFF000000
    }
}

private func invertColor(_ color: UInt) -> UInt {
    let a = (color >> 24) & 0xFF
    var r = (color >> 16) & 0xFF
    var g = (color >> 8) & 0xFF
    var b = (color) & 0xFF
    
    r = 255 - r
    g = 255 - g
    b = 255 - b
    
    return (a << 24) | (r << 16) | (g << 8) | b
}
